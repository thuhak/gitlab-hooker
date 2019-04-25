#!/bin/env bash
if [[ $action == "add" ]]; then
    source /etc/harborrc
    sudo docker build $repo\#$tag --network host --build-arg HTTP_PROXY=http://proxy.nevint.com:8080 --build-arg HTTPS_PROXY=http://proxy.nevint.com:8080 -t $mirror/$namespace/$project:$tag
    if [[ $? != 0 ]]; then
        echo building image for $project:$tag failed | mail -s "docker image building failed" $user_email
    	exit 1
    fi
    harbor project-show $namespace >/dev/null 2>1
    if [[ $? == 0 ]];then
        echo "$namespace already exists"
    else
        harbor project-create $namespace
    fi
    sudo docker login $mirror -u $HARBOR_USERNAME -p $HARBOR_PASSWORD
    sudo docker push $mirror/$namespace/$project:$tag
    if [[ $user_email != "disable" ]]; then
    echo finish image building for $project:$tag | mail -s "docker image building finish" $user_email
    fi
fi