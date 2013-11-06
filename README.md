# Mamba (tripsta python lib) 

## Contents

* Application Configuration
* SoapClient for twisted


## Provided classes

### mamba.application.BasicApplication

`BasicApplication` is a class that can handle ini reading and bootstrapping of resources in a lazy way

example

    from __future__ import print_function, absolute_import, division
    from mamba.application import BasicApplication

    app = BasicApplication(application_env='test', ini_path='.', doc_root='.')

    print(app.config)

    class MyApp(BasicApplication):

        def init__MySQL(self):
            # do config
            return mysql

        init__mycallable = MyCallable()

