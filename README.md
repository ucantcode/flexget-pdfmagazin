    pdfmagazin urlrewriter
    Version 0.1
    Configuration
    pdfmagazin:
      filehosters_re:
        - novafile\.com/*
      parse: yes
    filehosters_re: Only add links that match any of the regular expressions 
      listed under filehosters_re.
    For example, to use jdownloader 2 as output, you would use the exec plugin:
    exec:
      - echo "text={{urls}}" >> "/path/to/jd2/folderwatch/{{title}}.crawljob"
