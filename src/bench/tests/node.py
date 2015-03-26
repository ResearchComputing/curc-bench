import jinja2
import os
import pkg_resources


TEMPLATE = jinja2.Template(
    pkg_resources.resource_string(__name__, 'node.job'),
    keep_trailing_newline=True,
)


def generate(node_list, reservation, prefix):
    for node in node_list:
        output_file = os.path.join(prefix, '{0}.job'.format(node))
        with open(output_file, 'w') as fp:
            fp.write(TEMPLATE.render(
                node_name = node,
                reservation_name = reservation,
            ))
