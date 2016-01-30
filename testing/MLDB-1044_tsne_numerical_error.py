#
# MLDB-1044_tsne_numerical_error.py
# Datacratic, 2015
# This file is part of MLDB. Copyright 2015 Datacratic. All rights reserved.
#
# this script should create an assertion error when training the t-SNE
#
mldb = mldb_wrapper.wrap(mldb) # noqa

conf = {
    "type": "beh.binary",
    "params": {
        "dataFileUrl": "file:///home/mailletf/first_party.beh.lz4"
    }
}
rez = mldb.put("/v1/datasets/first_party", conf)
mldb.log(rez)

# Produce a cut-down version of the dataset that is suitable for running t-SNE.
# We can only handle 100,000 points or so with t-SNE, and even a dataset that
# big will be hard to plot or read.  Here, we take 1/100 of the dataset based
# on the part of the hash not used by the tranching code.
conf = {
    "type": "transform",
    "params": {
        "inputData":
            "select * from first_party where (rowHash() / 32) % 500 = 0",
        "outputDataset": {
            "id": "first_party_reduced",
            "type": "beh.binary.mutable"
        }
    }
}
rez = mldb.put("/v1/procedures/reduce", conf)
mldb.log(rez)
rez = mldb.post("/v1/procedures/reduce/runs")
mldb.log(rez)

conf = {
    "type" : "svd.train",
    "params" : {
        "trainingData" : {"from" : {"id" : "first_party_reduced"}},
        "rowOutputDataset" : {
            "id" : "first_party_svd_embedded",
            "type" : "embedding"
        }
    }
}
rez = mldb.put("/v1/procedures/svd_first", conf)
mldb.log(rez)
rez = mldb.post("/v1/procedures/svd_first/runs")
mldb.log(rez)

conf = {
    "type" : "kmeans.train",
    "params" : {
        "trainingData" : "select * from first_party_svd_embedded",
        "outputDataset" : {
            "id" : "first_party_kmeans_clusters",
            "type" : "embedding"
        },
        "numClusters" : 5
    }
}
rez = mldb.put("/v1/procedures/first_party_kmeans", conf)
mldb.log(rez)
rez = mldb.post("/v1/procedures/first_party_kmeans/runs")
mldb.log(rez)

conf = {
    "type" : "tsne.train",
    "params" : {
        "trainingData" : {"from" : {"id" : "first_party_svd_embedded"}},
        "rowOutputDataset" : {
            "id" : "first_party_tsne_subembedded",
            "type" : "embedding"
        }
    }
}
rez = mldb.put("/v1/procedures/first_party_tsne", conf)
mldb.log(rez)
rez = mldb.post("/v1/procedures/first_party_tsne/runs")
mldb.log(rez)

mldb.script.set_return("success")