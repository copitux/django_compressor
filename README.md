Django Compressor with Compass project support
======================================

Added `comprass` template tag to merge _django_compressor_ behaviour with precompile
compass files.
It differs with `CompassFilter` in the structure of statics in project.

While with `CompassFilter` you link each `*.sass` files and force to compress (because 
need precompile), with `comprass` tag you link each `*.css` files like you would do with 
normal projects and compile compass project before compressor and render.

Philosofy behind that is a __good__ structure of statics and __config compass file__

Example
-------

#### config.rb
Created by `compass create` or manually. Attach static structure dir
See @doc: http://compass-style.org

#### Dir structure inside `STATIC_ROOT` (django 1.3)

    /compass/print.sass
            /screen.sass
     config.rb
    /css/print.css
        /screen.css
        /extra.css

_Note: Of course `css` dir is populate by __compass___

#### Template example
    {% comprass %}
      <link href="{{ STATIC_PREFIX }}css/screen.css" media="screen, projection" rel="stylesheet" type="text/css" />
      <link href="{{ STATIC_PREFIX }}css/print.css" media="print" rel="stylesheet" type="text/css" />
      <link href="{{ STATIC_PREFIX }}css/extra.css" media="print" rel="stylesheet" type="text/css" />
      <style type="text/css">
        * { color: red !important; }
      </style>
    {% endcomprass %}

Settings config
---------------

    COMPASS_ENABLED [default: DEBUG]

    COMPASS_CONFIG [default: 'config.rb']
    Compass config file inside STATIC_ROOT

    COMPASS_WHERE [default: basename(COMPASS_CONFIG)]
    Where compass compile will be execute, attached to config compass file

    COMPASS_BINARY [default: 'compass']
