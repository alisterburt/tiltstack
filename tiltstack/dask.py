from os import PathLike

from dask_ctl import get_cluster

from dask.distributed import Client


def create_cluster(specification_file: PathLike) -> Client:
    cluster = get_cluster(str(specification_file))
    client = Client(cluster)
    return cluster
