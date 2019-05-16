# Macca Matching

This repository contains two things:

- A `Dockerfile`, which installs [scikit-learn](http://scikit-learn.org/stable/) with [miniconda](http://conda.pydata.org/miniconda.html), and a few [pip](https://pip.pypa.io/en/stable/) dependencies.
- A [Flask](http://flask.pocoo.org) `webapp`, which utilizes basic functionality of `scikit-learn`.


## ☤ Deploy this Application:

     $ heroku plugins:install heroku-container-registry
     $ heroku container:login
     
     $ git clone https://github.com/brotherko/Macca-matching
     $ cd Macca-matching
     
     $ heroku create
     $ heroku container:push web
