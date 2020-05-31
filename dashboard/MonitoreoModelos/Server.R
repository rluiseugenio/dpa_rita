shinyServer(function(input, output, session) {
  
  { 
    updateSelectizeInput(session = session, 'vuelo', 
                  choices = catalogo_vuelos,
                  selected = catalogo_vuelos$value[1], server = TRUE)
    updateSelectizeInput(session = session, 'wac', 
                    choices = catalogo_wac,
                    selected = catalogo_wac$value[1], server = TRUE)
  }
  
  source('source/serverModelos.R', local=TRUE, encoding = "utf-8")
  source('source/serverBias.R', local=TRUE, encoding = "utf-8")
  source('source/serverInfo.R', local=TRUE, encoding = "utf-8")
  

  
  })