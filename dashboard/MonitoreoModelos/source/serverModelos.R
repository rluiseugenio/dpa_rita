#MENUS actualizar-------
opciones_vuelo <- reactive({
  
  if(input$vuelo!=''){
  
  dbGetQuery(con2,sprintf("select distinct distance from
                                      predictions.train
                                        where flight_number = '%s'",
                          input$vuelo)) %>% 
      rbind(  dbGetQuery(con2,sprintf("select distinct distance from
                                      predictions.test
                                      where flight_number = '%s'",
                                      input$vuelo))) %>% 
    unique %>% 
    as_tibble %>% 
    mutate(label = paste(distance,'Km')) %>% 
    select(value = distance, label)
  }
})

observeEvent(input$vuelo,{

  opciones <-opciones_vuelo()
  
  updateSelectizeInput(session = session, 'distMon', 
                    choices = opciones,
                    selected = opciones$value[1], server = TRUE)
})

#####Reactivos ----------

modelos_react <- reactive({

    tt <- dbGetQuery(con2,sprintf("select distance,
                                  label_value as observado,
                                  score as prediccion,
                                  fecha
                           from predictions.train
                           where distance = '%s'
                           and flight_number = '%s'",
                                  input$distMon,#
                                  input$vuelo)) %>% 
      mutate(flight_number = input$vuelo) %>% 
      select(flight_number, distance, observado, prediccion,
             fecha)
    
    kk <-  dbGetQuery(con2,sprintf("select distance,
                                  flight_number,
                                  prediction as prediccion,
                                  fecha
                           from predictions.test
                           where distance = '%s'
                           and flight_number = '%s'",
                                  input$distMon,#
                      input$vuelo)) %>% 
      mutate(observado = NA) %>% 
      select(flight_number, distance, observado, prediccion,
             fecha)

res <- tt %>% 
  rbind(kk) %>% 
  as_tibble%>% 
  mutate(dia = substr(fecha,7,8),
         mes = substr(fecha,5,6),
         ano = substr(fecha,1,4),
         fecha = ymd(paste0(ano,'-',mes,'-',dia))) %>% 
  arrange(fecha) %>% 
  split(.$fecha) %>% 
  map(~reciente(.)) %>% 
  bind_rows() %>% 
  mutate(prediccion = sample(c(0,1),
                            nrow(.),
                            replace =TRUE,
                            prob = c(.2,.8)),
         ruido = runif(nrow(.),-0.25,.25),
         ef = abs(as.numeric(prediccion)-observado),
         ef = ifelse(ef==0,NA,ef),
         prediccion = as.numeric(prediccion),
         observado = observado)
  
res
})

dist_react <- reactive({
  tt <- dbGetQuery(con2,"select distance, count(*) as conteo
                   from predictions.train
                   group by distance") %>% 
    mutate(fuente = 'TRAIN')
  
kk <- dbGetQuery(con2,"select distance, count(*) as conteo
                   from predictions.test
                   group by distance")   %>% 
  mutate(fuente = 'TEST')
res <- tt %>% 
  rbind(kk) %>% 
  mutate_if(bit64::is.integer64,as.integer) %>% 
  group_by(fuente) %>% 
  mutate(porcentaje = 100*conteo/sum(conteo)) %>% 
  ungroup %>% 
  mutate(distance = paste0(distance,' Km'))

res

})


#Gráficas ------------

output$modelos_plot <- renderEcharts4r({
  
  if(input$refresh=='Activado'){
    invalidateLater(30000,session=session)
  }

  GLOBAL_TS_filter <- modelos_react() 

  GLOBAL_TS_filter %>% 
    e_charts(fecha) %>%
    e_scatter(prediccion, color = 'gray',
              # tooltip = list(show = FALSE)
              ) %>%
    e_effect_scatter(observado,
                     ef, color ='salmon',
                     # tooltip = list(show = FALSE)
                     ) %>%      
    e_tooltip(trigger = 'axis',
              axisPointer = list(
                type = "cross"
              ))%>%
    e_legend(type="scroll") %>%
    e_toolbox(orient= 'vertical', itemSize= 20, itemGap= 20) %>%
    e_toolbox_feature(feature= "saveAsImage") %>%
    e_toolbox_feature(feature= "restore") %>%
    e_toolbox_feature(feature="dataView") %>%
    e_toolbox_feature(feature="dataZoom",yAxisIndex='none') %>%
    e_datazoom(x_index = 0, type = "slider") %>%
    e_datazoom(x_index = 0, type = "inside") %>%
    e_datazoom() %>% 
    e_title(paste0('Número de vuelo ',input$vuelo),
            paste0('Distancia de ',input$distMon,' Km')) 
  
})

#Botón para actualizar
react <- reactive( {
 data.frame(fecha = ymd('2020-01-12'),
            prediccion = 2,
            observado = -1,
            ef = 1)
})

observeEvent(input$add, {
  echarts4rProxy("modelos_plot") %>%
     e_append1_p(0,react(), fecha, prediccion) %>% 
     e_append2_p(1, react(), fecha, observado, ef)
})




output$distribucion_train_plot <- renderEcharts4r({
 
  
  # browser()
  colors <- cbb.s
  
  gr <- dist_react() %>%
    filter(fuente == 'TRAIN') %>% 
    mutate(distance = ifelse(porcentaje >= 4, distance, "OTRAS")) %>%
    group_by(distance) %>%
    summarise(porcentaje = sum(porcentaje),
              conteo = sum(conteo)) %>%
    ungroup() 
  
  if(nrow(gr)==0){
    data.frame(model = "Sin Data",
               carb = 1,
               stringsAsFactors = F) %>% 
      e_charts(model) %>% 
      e_pie(carb, radius = c("50%", "70%")) %>% 
      e_title("Sin Data")%>% 
      e_theme("macarons")
  }else{  
    
    gr %>%
      e_charts(distance) %>%
      e_pie(porcentaje, radius = c("50%", "70%")) %>%
      e_labels(formatter= c("{b}: {d}%")) %>%
      e_tooltip(trigger = "item") %>%
      e_legend(type="scroll",bottom='bottom') %>%
      e_theme("macarons") %>% 
      e_title('Distribución de distancias',
              "Datos de Entrenamiento")
    
  }
})

output$distribucion_test_plot <- renderEcharts4r({
  
  
  
  colors <- cbb.s
  
  gr <- dist_react() %>%
    filter(fuente == 'TEST') %>% 
    mutate(distance = ifelse(porcentaje >= 4, distance, "OTRAS")) %>%
    group_by(distance) %>%
    summarise(porcentaje = sum(porcentaje),
              conteo = sum(conteo)) %>%
    ungroup() 
  
  
  if(nrow(gr)==0){
    data.frame(model = "Sin Data",
               carb = 1,
               stringsAsFactors = F) %>% 
      e_charts(model) %>% 
      e_pie(carb, radius = c("50%", "70%")) %>% 
      e_title("Sin Data")%>% 
      e_theme("macarons")
  }else{  
    
    gr %>%
      e_charts(distance) %>%
      e_pie(porcentaje, radius = c("50%", "70%")) %>%
      e_labels(formatter= c("{b}: {d}%")) %>%
      e_tooltip(trigger = "item") %>%
      e_legend(type="scroll",bottom='bottom') %>%
      e_theme("macarons") %>% 
      e_title('Distribución de distancias',
              "Datos de Prueba")
    
  }
})

#Tablas------------------------------------------------

output$alertas_out <- renderDT({
   # if( input$distMon=="1045"){browser()}
  
  data <- modelos_react() %>% 
    filter(!is.na(ef)) %>% 
    select(fecha,
           flight_number,
           distance,observado,
           prediccion)
  
  if (!nrow(data)>0) {
    data <- data.frame(EstadoActual = 'Sin data')    
    
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

output$modelos_out <- renderDT({

  
  data <- modelos_react() %>% 
    select(-ruido)
  
  if (!nrow(data)>0) {
    data <- data.frame(EstadoActual = 'Sin data')    
    
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


