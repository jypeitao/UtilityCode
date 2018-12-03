#!/bin/bash
repo forall -c git clean -df
repo forall -c git reset --hard HEAD
repo start wk1 --all
repo forall -c "git branch | sed -e /^*/d | xargs git branch -D"
