from compressor.conf import settings
from compressor.base import Compressor, SOURCE_HUNK, SOURCE_FILE
from compressor.exceptions import UncompressableFileError
from django.template.loader import render_to_string


class CssCompressor(Compressor):
    template_name = "compressor/css.html"
    template_name_inline = "compressor/css_inline.html"

    def __init__(self, content=None, output_prefix="css"):
        super(CssCompressor, self).__init__(content, output_prefix)
        self.filters = list(settings.COMPRESS_CSS_FILTERS)
        self.type = 'css'

    def split_contents(self):
        if self.split_content:
            return self.split_content
        self.nodes_to_output = {}
        for elem in self.parser.css_elems():
            data = None
            elem_name = self.parser.elem_name(elem)
            elem_attribs = self.parser.elem_attribs(elem)
            if elem_name == 'link' and elem_attribs['rel'] == 'stylesheet':
                try:
                    basename = self.get_basename(elem_attribs['href'])
                    filename = self.get_filename(basename)
                    data = (SOURCE_FILE, filename, basename, elem)
                except UncompressableFileError:
                    if settings.DEBUG:
                        raise
            elif elem_name == 'style':
                data = (SOURCE_HUNK, self.parser.elem_content(elem), None, elem)
            if data:
                self.split_content.append(data)
                media = elem_attribs.get('media', None)
                ie = elem_attribs.get('ie', None)
                # filter by media & IE conditionals
                if ie:
                    try:
                        self.nodes_to_output[ie][media].split_content.append(data)
                    except KeyError as err:
                        node = CssCompressor(str(elem))
                        node.split_content.append(data)
                        if err[0] == ie:
                            self.nodes_to_output[ie] = {media: node}
                        elif err[0] == media:
                            self.nodes_to_output[ie].update({media: node})
                else:
                    try:
                        self.nodes_to_output[media].split_content.append(data)
                    except KeyError: 
                        node = CssCompressor(str(elem))
                        node.split_content.append(data)
                        self.nodes_to_output[media] = node 

        return self.split_content

    def output(self, *args, **kwargs):
        # Populate self.split_content
        if (settings.COMPRESS_ENABLED or settings.COMPRESS_PRECOMPILERS or
                kwargs.get('forced', False)):
            self.split_contents()
            if hasattr(self, 'nodes_to_output'):
                ret = []
                for block, to_split in self.nodes_to_output.items():
                    if block.startswith('[if'):
                        ietag = []
                        for media, subnode in to_split.items():
                            subnode.extra_context.update({'media': media})
                            ietag.append(subnode.output(*args, **kwargs))
                        #surround with ietags, can't go to render_output
                        ret.append(render_to_string('compressor/iecss_file.html', {
                                'ie': block,
                                'content': ietag
                            })
                        )
                    else:
                        to_split.extra_context.update({'media': block})
                        ret.append(to_split.output(*args, **kwargs))
                return ''.join(ret)
        return super(CssCompressor, self).output(*args, **kwargs)
