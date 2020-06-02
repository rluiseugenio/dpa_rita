#distancias dado origin wacc --------------
opciones_bias <- reactive({
  
  if(input$wac!=''){
  dbGetQuery(con2,sprintf("select distinct distance from
                                      predictions.train 
                                      where originwac = '%s'",input$wac)) %>% 
    unique %>% 
    as_tibble %>% 
    mutate(label = paste(distance,'Km')) %>% 
    select(value = distance, label)
  }
})

observeEvent(input$wac,{
  opciones <- opciones_bias()
  
  
  updateSelectizeInput(session = session, 'distBias', 
                    choices = opciones,
                    selected = opciones$value[1], server = TRUE)
})



#####Reactivos ----------
#data para bias
kk_react <- reactive({
  req(input$wac)
  req(input$distBias)
  
  dbGetQuery(con2,sprintf("select score, label_value, count(*) as count
             from predictions.train 
             where originwac='%s'
             and distance = '%s'
             group by score, label_value",
                   input$wac,
                   input$distBias)) 
})

bias_react <- reactive({

  ll <- dbGetQuery(con2,"select * from metadatos.bias") %>% 
    as_tibble %>% 
    mutate(dia = substr(fecha,7,8),
           mes = substr(fecha,5,6),
           ano = substr(fecha,1,4),
           fecha = ymd(paste0(ano,'-',mes,'-',dia))) %>% 
    arrange(fecha) %>% 
    split(.$fecha) %>% 
    map(~reciente2(.)) %>% 
    bind_rows() %>%
    arrange(-as.numeric(fecha))%>% 
    head(1) 
  
  
q1 <- ll %>% 
    select(contains('q1')) %>% 
    purrr::set_names(nm = c('atributo', 'fdr')) 
  
q2 <- ll %>% 
      select(contains('q2')) %>% 
      purrr::set_names(nm = c('atributo', 'fdr')) 
    
  
q3 <- ll %>% 
      select(contains('q3')) %>% 
      purrr::set_names(nm = c('atributo', 'fdr')) 
    
q4 <- ll %>% 
      select(contains('q4')) %>% 
      purrr::set_names(nm = c('atributo', 'fdr')) 
    
res <- rbind(q1,q2,q3,q4)
  
})

#Gráficas ------------
#matrix de confusión

output$confmat_plot <- renderEcharts4r({
  
  kk <-  kk_react()
  
  kk %>% 
    mutate(count =round(100*count/sum(count),
                        digits = 2))%>% 
    e_charts(score) %>% 
    e_heatmap(label_value, count) %>% 
    e_visual_map(count) %>% 
    e_title("Matriz de confusión",
            paste0('Para el código de origen ',input$wac,
                   ' con viajes de distancia ',input$distBias,' Km.')) %>% 
    e_tooltip()
  
})

output$barras_plot <- renderEcharts4r({

  kk <- bias_react()
  
  
  kk  %>% 
    e_charts(atributo) %>% 
    e_bar(fdr, name = 'FPR Disparity') %>% 
    e_flip_coords() %>% 
    e_tooltip( formatter = e_tooltip_item_formatter(style = "decimal",
                                                    digits = 2)    )
  
})

#Tablas------------------------------------------------

#Fairness
output$fb_out <- renderDT({
  
  
  data <- bias_react() %>% 
    select(atributo, fpr = fdr)
  
  if (!nrow(data)>0) {
    data <- data.frame(EstadoActual = 'Sin alertas.')    
    
    DT::datatable(data, 
                  rownames = FALSE,
                  extensions = c( 'ColReorder','Buttons'),
                  options = list(scrollX = TRUE,
                                 colReorder = TRUE)) 
    
  }else{
    DT::datatable(data, 
                  rownames = FALSE,
                  extensions = c( 'ColReorder','Buttons'),
                  options = list(scrollX = TRUE,
                                 colReorder = TRUE))
  }
  
})


