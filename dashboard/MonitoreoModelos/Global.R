library(bs4Dash)
library(shinycssloaders)
library(RPostgres)
library(dplyr)
library(tidyr)
library(stringr)
library(echarts4r)
library(DT)
library(lubridate)
library(scales)
library(shinyWidgets)
library(purrr)
library(magrittr)
library(shiny)




con2 <- DBI::dbConnect(RPostgres::Postgres(),
                      
                      dbname = 'postgres',
                      
                      host = "postgres.ctruwx4duee9.us-east-1.rds.amazonaws.com",
                      
                      port = "5432",
                      
                      user = "postgres",
                      
                      password = "cusbQnXvCyTHbK7LJGnV")


source('source/FunctionsUI.R', local=TRUE, encoding = "utf-8")



Sys.setlocale(locale="es_ES.UTF-8")
#Sys.setlocale("LC_TIME", "Spanish") 

#MENUS UI
dbSendQuery(con2, "set timezone = 'America/Mexico_City';")

options(DT.options = list(pageLength = 25, 
                          language = list(url = '//cdn.datatables.net/plug-ins/1.10.11/i18n/Spanish.json'),
                          searchHighlight = TRUE,
                          scrollX = TRUE,
                          keys = TRUE,
                          initComplete = JS(
                            "function(settings, json) {",
                            "$(this.api().table().header()).css({'background-color': '#0179FE', 'color': '#fff'});",
                            "}"
                          ),
                          dom = 'lBfrtip',
                          buttons = list(
                            list(extend='colvis',text='Columnas'),
                            list(extend='copy', text='Copiar'), 
                            list(extend = 'collection', buttons = c('csv', 'excel', 'pdf'), text = 'Descargar')
                          ),
                          lengthMenu = c(25, 50, 100, 200)))

catalogo_wac <- dbGetQuery(con2,"select distinct originwac from
                                      predictions.train ") %>% 
  as_tibble %>% 
  mutate(label = paste('Código de origen:',originwac)) %>% 
  select(value = originwac, label)

catalogo_vuelos <- dbGetQuery(con2,"select distinct flight_number from
                                      predictions.test ") %>% 
  rbind(dbGetQuery(con2,"select distinct flight_number from
                                      predictions.train ")) %>% 
  as_tibble %>% 
  mutate(label = paste('Número de vuelo:',flight_number)) %>% 
  select(value = flight_number, label)

reciente <- function(x){
  x %<>% 
    mutate(aux = 1:nrow(.)) %>% 
    # filter(!is.na(observado)) %>% 
    filter(aux == 1) %>% 
    select(-aux)
}

reciente2 <- function(x){
  x %<>% 
    mutate(aux = 1:nrow(.)) %>% 
    filter(aux == 1) %>% 
    select(-aux)
}

cbb.s <- c("#999999", "#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7",
           "#8DD3C7","#FFFFB3","#BEBADA","#FB8072","#80B1D3","#FDB462","#B3DE69","#FCCDE5",
           "#D9D9D9","#BC80BD","#CCEBC5","#A6CEE3","#1F78B4","#B2DF8A","#33A02C","#FB9A99","#E31A1C",
           "#FDBF6F","#FF7F00","#CAB2D6","#6A3D9A","#FFFF99","#1B9E77","#D95F02","#7570B3","#E7298A",
           "#66A61E","#E6AB02","#A6761D","#666666","#7FC97F","#BEAED4","#FDC086","#386CB0",
           "#F0027F","#BF5B17","#66C2A5","#FC8D62","#8DA0CB","#E78AC3","#A6D854","#FFD92F","#E5C494","#B3B3B3")
