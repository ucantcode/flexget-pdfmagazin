<h2>Brief</h2>
    This is the python code for flexget. Put it into the "/usr/local/lib/python2.7/dist-packages/flexget/plugins/sites/".   
<h2>Configuration</h2>

    pdfmagazin:
      filehosters_re:
        - novafile\.com/*
      parse: yes
    exec:
      - echo "text={{urls}}" >> "/path/to/jd2/folderwatch/{{title}}.crawljob"
