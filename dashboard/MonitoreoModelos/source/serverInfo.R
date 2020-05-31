
output$info66 <- renderUI({
  stra <- paste('A continuación se muestra la información del mejor modelo')
})

#Catálogo de Respuestas
output$info3 <- renderDT({

data <- dbGetQuery(con2,"select * 
                   from metadatos.models 
                   order by f1 desc limit 1;") %>% 
  select(model_name, objetivo, hyperparams, f1, train_time, train_nrows,
         test_split)
 
    DT::datatable(data, 
                  rownames = FALSE,
                  extensions = list(),
                  options = list(scrollX = TRUE,
                                 colReorder = TRUE)) 
 
})