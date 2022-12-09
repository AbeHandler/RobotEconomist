import os
from re import I

from src.pipelines.pipeline_config import PipelineConfig


class AwsHelper(object):

    def clean_bucket(self, config: PipelineConfig):

        cmd = f'aws s3 ls s3://{config.bucket_name}'

        cmd = cmd + "| awk -F' ' '{print $4}'"

        cmd = cmd + f'| parallel -j 1 "aws s3 rm s3://{config.bucket_name}/'

        cmd = cmd + '{}"'

        print(cmd)

        print("[*] Code is too dangerous to run programmatically, you run it")


    def publish_report(self, output_name: str):

        svg_cmd = f'aws s3 cp reports/{output_name}.svg s3://abha4861iv/{output_name}.svg --acl public-read'
        os.system(svg_cmd)
        html_cmd = f'aws s3 cp reports/{output_name}.html s3://abha4861iv/{output_name}.html --content-type "text/html" --acl public-read'
        os.system(html_cmd)
        png_cmd = f'aws s3 cp reports/{output_name}.svg s3://abha4861iv/{output_name}.png --content-type "text/html" --acl public-read'
        os.system(png_cmd)

if __name__ == "__main__":

    helper = AwsHelper()

    config = PipelineConfig(corpus="ivis")

    helper.clean_bucket(config)