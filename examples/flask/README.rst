========================================
 limiterapp - Flask Example Application
========================================

This is a fairly simple application that doesn't properly authenticate
anything and only checks authorization credentials for the purpose of
throttling.


Running the Application
=======================

See our documentation_ for more details on this example and how to set it up.

.. code::

   pipenv run gunicorn -w4 limiterapp.views:app


What to Expect
==============

.. code::

   ~/s/rush ❯❯❯ curl -i http://127.0.0.1:8000/
   HTTP/1.1 200 OK
   Server: gunicorn/19.9.0
   Date: Sat, 29 Dec 2018 15:47:49 GMT
   Connection: close
   Content-Type: text/plain
   X-RateLimit-Limit: 50
   X-RateLimit-Remaining: 39
   X-RateLimit-Reset: 2018-12-29T15:59:44.247025+0000
   X-RateLimit-Retry: 2018-12-29T15:47:48.067240+0000
   Content-Length: 26

   ~/s/rush ❯❯❯ curl -i http://test:test@127.0.0.1:8000/
   HTTP/1.1 200 OK
   Server: gunicorn/19.9.0
   Date: Sat, 29 Dec 2018 15:46:02 GMT
   Connection: close
   Content-Type: text/html; charset=utf-8
   X-RateLimit-Limit: 5000
   X-RateLimit-Remaining: 5499
   X-RateLimit-Reset: 2018-12-29T15:45:53.956355+0000
   X-RateLimit-Retry: 2018-12-29T15:46:01.095534+0000
   Content-Length: 21


.. links
.. _documentation:
   https://rush.readthedocs.io
