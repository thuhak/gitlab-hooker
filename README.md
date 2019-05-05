# gitlab webhook转换器

接收gitlab webhook，并转换成jenkins调用

## 配置说明


```yaml
server:
  token: token                 #gitlab中需要填写的token

taghandler:
  project1:                    #gitlab中的url为/tag/project1
    jenkins_url: Jenkins_1     #对应的jenkins url
    jenkins_token: build       #对应的jenkins token
  project2:
    jenkins_url: Jenkins_2
    jenkins_token: build
    trigger:                  #是否使用action过滤,add或者remove,用于仅在特定条件触发jenkins job
      - add
```

- 配置可以使用等价的json格式表示
- 可以动态增加监听的url