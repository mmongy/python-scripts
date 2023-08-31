
# https://gist.github.com/will-moore/a9f90c97b5b6f1a0da277a5179d62c5a

import argparse
import sys
import os

from omero.cli import cli_login
from omero.gateway import BlitzGateway

from omero.plugins.download import DownloadControl

OBJ_INFO = "obj should be 'Project:ID' or 'Dataset:ID'"

"""
Usage:

python download_pdi.py Project:123 my_project_directory
"""

def download_datasets(conn, datasets, target_dir):

    for dataset in datasets:
        print("Downloading Dataset", dataset.id, dataset.name)
        dc = DownloadControl()
        dataset_dir = os.path.join(target_dir, dataset.name)
        os.makedirs(dataset_dir, exist_ok=True)

        for image in dataset.listChildren():
            if image.getFileset() is None:
                print("No files to download for Image", image.id)
                continue
            # image_dir = os.path.join(dataset_dir, image.name)
            # If each image is a single file, or are guaranteed not to clash
            # then we don't need image_dir. Can use dataset_dir instead
            
            fileset = image.getFileset()
            if fileset is None:
                print('Image has no Fileset')
                continue
            dc.download_fileset(conn, fileset, dataset_dir)


def download_object(cli, args):

    conn = BlitzGateway(client_obj=cli._client)
    conn.SERVICE_OPTS.setOmeroGroup(-1)

    obj = args.obj
    try:
        obj_id = int(obj.split(":")[1])
        obj_type = obj.split(":")[0]
    except:
        print(OBJ_INFO)

    parent = conn.getObject(obj_type, obj_id)
    if parent is None:
        print("Not Found:", obj)

    datasets = []
    target_dir = args.target

    if obj_type == "Dataset":
        datasets.append(parent)
    elif obj_type == "Project":
        datasets = list(parent.listChildren())
        target_dir = os.path.join(target_dir, parent.getName())
    else:
        print(OBJ_INFO)

    print("Downloading to ", target_dir)

    download_datasets(conn, datasets, target_dir)


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('obj',
        help="Download object: 'Project:ID' or 'Dataset:ID'")
    parser.add_argument('target',
        help="Directory name to download into")
    args = parser.parse_args(argv)

    with cli_login() as cli:
        download_object(cli, args)

if __name__ == '__main__':
    main(sys.argv[1:])
