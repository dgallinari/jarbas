import re
from os import path
from tempfile import NamedTemporaryFile
from urllib.request import urlretrieve

from django.conf import settings
from django.core.management.base import BaseCommand
from markdown import markdown
from mdx_gfm import GithubFlavoredMarkdownExtension as GitHubMarkdown


class Command(BaseCommand):
    help = 'Download the updated version of CEAP variables description table'

    def add_arguments(self, parser):
        parser.add_argument(
            '--source', '-s', dest='source', default=None,
            help='Data directory of Serenata de Amor (datasets source)'
        )

    def handle(self, *args, **options):
        origin = 'https://{}.amazonaws.com/{}/{}-ceap-datasets.md'.format(
            settings.AMAZON_S3_REGION,
            settings.AMAZON_S3_BUCKET,
            settings.AMAZON_S3_DATASET_DATE
        )
        target = path.join(settings.ASSETS_ROOT, 'ceap-datasets.html')
        tmp = NamedTemporaryFile()

        self.stdout.write('Downloading markdown from ' + origin)
        urlretrieve(origin, filename=tmp.name)

        self.stdout.write('Converting markdown to HTML')
        with open(tmp.name) as md:
            source = markdown(md.read(), extensions=[GitHubMarkdown()])

        self.stdout.write('Applying GitHub CSS styles')
        css_path = path.join(
            settings.BASE_DIR,
            'node_modules',
            'github-markdown-css',
            'github-markdown.css'
        )
        with open(css_path) as css:
            style = css.read()

        self.stdout.write('Saving HTML to ' + target)
        with open(target, 'w') as html:
            body_styles = ''.join((
                'box-sizing: border-box;',
                'min-width: 200px;',
                'max-width: 980px;',
                'margin: 0 auto;',
                'padding: 45px;'
            ))
            structure = """
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <title>{}</title>
                    <style>{}</style>
                </head>
                <body class="markdown-body" style="{}">
                  {}
                </body>
                </html>
            """

            title = 'Quota for Exercising Parliamentary Activity (CEAP)'
            full_source = structure.format(title, style, body_styles, source)
            html.write(minify(full_source))


def minify(html):
    return re.compile(r'(^[\s]*)|\n[\s]*').sub('', html)
