from abc import ABC, abstractmethod
from typing import Dict, List, Set


from src.corpus.paper import Paper
from src.corpus.corpus import Corpus
from src.dag.dag import Dag
from src.dag.edge import Edge
from src.dag.vertex import Vertex
from itertools import combinations
from src.tagger import Tag
import json


class AbstractTagCluster(ABC):

    def __init__(self) -> None:
        self.tags: List[Tag] = []

    def add(self, tag) -> None:
        self.tags.append(tag)

    def get_ids(self) -> List[str]:
        '''
        Get unique ids of papers in cluster
        '''
        out = set()
        for tag in self.tags:
            out.add(tag.origin_paper_id)

        # convert type and sort
        outl = [o for o in out]
        outl.sort()

        return outl

    @abstractmethod
    def get_cluster_name(self) -> str:
        pass

    @abstractmethod
    def get_cluster_type(self) -> str:
        pass


class ExactStringTagCluster(AbstractTagCluster):

    def get_cluster_name(self) -> str:
        return self.tags[0].literal_text

    def get_cluster_type(self) -> str:
        return self.tags[0].tag


class AbstractEdgeResolver(ABC):

    def __init__(self, config: str = "config/config.json") -> None:
        with open(config, "r") as inf:
            self.config = json.load(inf)

    @abstractmethod
    def has_an_edge(self, A: AbstractTagCluster, B: AbstractTagCluster) -> str:
        pass

    @abstractmethod
    def get_edges(self, A: AbstractTagCluster, B: AbstractTagCluster, cluster2vertex: Dict[AbstractTagCluster, Vertex]) -> List[Edge]:
        '''
        if multiple relationships between variables are asserted in multiple papers
        then there are multiple edges
        '''
        pass


class EdgeBuilder(AbstractEdgeResolver):

    def intersecting_ids(self, A: AbstractTagCluster, B: AbstractTagCluster) -> set:
        A_ids: List[str] = A.get_ids()
        B_ids: List[str] = B.get_ids()
        return set(A_ids) & set(B_ids)

    def has_an_edge(self, A: AbstractTagCluster, B: AbstractTagCluster):
        '''
        If the clusters have a paper in common there is an edge
        '''
        return len(self.intersecting_ids(A, B)) > 0

    def get_edges(self, A: AbstractTagCluster, B: AbstractTagCluster, cluster2vertex: Dict[AbstractTagCluster, Vertex]) -> List[Edge]:
        intersecting_ids = self.intersecting_ids(A, B)
        out: List[Edge] = []
        for id_ in intersecting_ids:
            tags_in_A = [o for o in A.tags if o.origin_paper_id == id_]
            tags_in_B = [o for o in B.tags if o.origin_paper_id == id_]

            for a in tags_in_A:
                for b in tags_in_B:

                    # the cluster may be at the tip or tail of the arrow in the dag so need to check both directions
                    if a.tag == self.config["vertexes"]["instrument"] and b.tag == self.config["vertexes"]["regressor"]:
                        out.append(Edge(
                            cluster2vertex[A], cluster2vertex[B], label=self.config["edges"]["instruments_label"]))
                    if b.tag == self.config["vertexes"]["instrument"] and a.tag == self.config["vertexes"]["regressor"]:
                        out.append(Edge(
                            cluster2vertex[B], cluster2vertex[A], label=self.config["edges"]["instruments_label"]))

                    if a.tag == self.config["vertexes"]["regressor"] and b.tag in [self.config["vertexes"]["outcome"], self.config["vertexes"]["regressor"]]:
                        out.append(Edge(
                            cluster2vertex[A], cluster2vertex[B], label=self.config["edges"]["affects_label"]))
                    if b.tag == self.config["vertexes"]["regressor"] and a.tag in [self.config["vertexes"]["outcome"], self.config["vertexes"]["regressor"]]:
                        out.append(Edge(
                            cluster2vertex[B], cluster2vertex[A], label=self.config["edges"]["affects_label"]))

                    if a.tag == self.config["vertexes"]["regressor"] and b.tag in [self.config["vertexes"]["regressor"], self.config["vertexes"]["regressor"]]:
                        out.append(Edge(
                            cluster2vertex[A], cluster2vertex[B], label=self.config["edges"]["affects_label"]))
                    if b.tag == self.config["vertexes"]["regressor"] and a.tag in [self.config["vertexes"]["regressor"], self.config["vertexes"]["regressor"]]:
                        out.append(Edge(
                            cluster2vertex[B], cluster2vertex[A], label=self.config["edges"]["affects_label"]))

        return out


class AbstractTagToVertexCorefResolver(ABC):

    '''
    Say paper 1 and paper 2 use weather as an IV
    We need a way to get one vertex in the dag for
    these papers. Treat it as a coref/clustering problem
    '''

    def __init__(self) -> None:
        super().__init__()
        self.clusters: List[ExactStringTagCluster] = []

    @abstractmethod
    def is_coreferent(self, tag1: Tag, tag2: Tag) -> bool:
        pass

    def init_cluster(self, cluster: AbstractTagCluster) -> None:
        self.clusters.append(cluster)

    def is_in_some_cluster(self, tag: Tag) -> bool:
        return any(self.is_in_this_cluster(tag, cluster) for cluster in self.clusters)

    def is_in_this_cluster(self, tag: Tag, cluster: ExactStringTagCluster) -> bool:
        for already_clustered in cluster.tags:
            if self.is_coreferent(tag, already_clustered):
                return True
        return False

    def clusterN_squared(self, tags: List[Tag]) -> List[AbstractTagCluster]:
        '''naively cluster; intractable for big N'''
        for tag in tags:
            if self.is_in_some_cluster(tag):
                for cluster in self.clusters:
                    if self.is_in_this_cluster(tag, cluster):
                        cluster.add(tag)
            else:
                cluster: ExactStringTagCluster = ExactStringTagCluster()
                cluster.add(tag)
                self.init_cluster(cluster)
        return self.clusters


class ExactStringTagToVertexCorefResolver(AbstractTagToVertexCorefResolver):

    def is_coreferent(self, tag1: Tag, tag2: Tag) -> bool:
        '''
        Determine coref via exact string similiarity

        Note that the same string may have different types in different
        papers. For instance, paper 1 may use voting as a regressor
        and paper 2 may use voting as an outcome. We will give them
        a single vertex in the dag, according to the logic in this
        method
        '''
        if tag1.literal_text == tag2.literal_text:
            return True
        else:
            return False


class AbstractTag2Vertex(ABC):

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def tag2vertex(self, tag: Tag) -> Vertex:
        pass


class VertexBuilder(object):
    '''
    Convert a tag to a vertex for the dag

    There could be other ways to do this so I made a class
    '''

    def __init__(self) -> None:
        self.total_vertexes = 0

    def cluster2vertex(self, cluster: AbstractTagCluster) -> Vertex:
        name = cluster.get_cluster_name()
        ids_ = cluster.get_ids()
        out = Vertex(variable_name=name,
                     papers_id=ids_,
                     vertex_id=self.total_vertexes)
        self.total_vertexes += 1
        return out


class GraphBuilder(object):

    '''
    Handles the logic of converting tags from a tagger to
    vertexes and edges in a DAG

    Tags themselves are too concrete to be parts of a DAG. You might want to
    merge dupe tags for instance
    '''

    def get_papers(self) -> List[Paper]:
        return [paper for paper in self.corpus.papers]

    def get_vertexes_in_paper(self, paper: Paper, vertexes_from_corpus: List[Vertex]) -> List[Vertex]:
        # note that the logic below is that the paper_id has to be *in* the papers id
        # Some vertexes can be associated w/ more than one vertex
        return [o for o in vertexes_from_corpus if paper.paper_id in o.papers_id]

    def get_all_pairs(self, vertexes: List[Vertex]) -> List[Vertex]:
        return [o for o in combinations(vertexes, 2)]

    def __init__(self, corpus: Corpus,
                 vertex_coref_resolver: ExactStringTagToVertexCorefResolver = ExactStringTagToVertexCorefResolver(),
                 config: str = "config/config.json") -> None:
        self.corpus = corpus
        with open(config, "r") as inf:
            self.config = json.load(inf)
            self.config_edges = self.config["edges"]
            self.config_vertexes = self.config["vertexes"]
            self.vertex_coref_resolver = vertex_coref_resolver
            self.valid_types = self.config.keys()

    def impute_vertexes(self, vertexes_in_corpus, corpus):  # type: ignore
        '''
        merge vertexes based on semantic similarity
        e.g. "rain" and "hurricane" are both kinds of weather
        '''
        raise NotImplementedError('not coded yet')

    def clusters_to_vertexes(self, tag_clusters: List[AbstractTagCluster],
                             vertex_maker: VertexBuilder = VertexBuilder()) -> Dict[AbstractTagCluster, Vertex]:
        '''
        Convert low-level tag clusters to vertexes for the DAG
        '''
        out: Dict[AbstractTagCluster, Vertex] = {}

        for cluster in tag_clusters:
            vertex = vertex_maker.cluster2vertex(cluster)
            out[cluster] = vertex

        return out

    def tags_to_dag(self, tags: List[Tag]) -> Dag:
        '''
        This method is why this class exists

        A spacy tagger returns spans of text, that is different from
        vertexes in a dag. Maybe you want to merge coreferent spans,
        maybe you want to add noisy vertexes based on semantic similiarity
        Lots of stuff. So basically you need an abstraction over the tags
        to the Dag. The Analyzer covers that step
        '''
        clusters: List[AbstractTagCluster] = self.vertex_coref_resolver.clusterN_squared(
            tags)
        cluster2vertex: Dict[AbstractTagCluster,
                             Vertex] = self.clusters_to_vertexes(clusters)
        edges: Set[Edge] = self.impute_edges_corpus(
            clusters_in_corpus=clusters, cluster2vertex=cluster2vertex)
        return Dag(vertexes=list(cluster2vertex.values()), edges=edges)

    def impute_edges_corpus(self, clusters_in_corpus: List[AbstractTagCluster],
                            cluster2vertex: Dict[AbstractTagCluster, Vertex],
                            resolver=EdgeBuilder()
                            ) -> Set[Edge]:
        '''
        The extractor will find *vertexes* such as what is the IV
        and what is the outcome. The edges have to be imputed
        for instance (IV, outcome, affects). This step can be
        rule-based for now but maybe someday you might want to
        do fancier kinds of imputation
        '''
        output: List[Edge] = []
        all_pairs = self.get_all_pairs(clusters_in_corpus)
        for cluster1, cluster2 in all_pairs:
            edges: List[Edge] = resolver.get_edges(
                cluster1, cluster2, cluster2vertex)
            output = output + edges
        return set(output)
