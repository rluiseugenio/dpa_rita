fechaBusquedaInput <- function(idInicio, idFin, idRef) {
  tagList(
  dateInput(
    idInicio,
    label = "Fecha Inicio:",
    value = NULL,
    format = "yyyy-mm-dd",
    startview = "day",
    language = "es"
  ),
  dateInput(
    idFin,
    label = "Fecha Fin:",
    value = NULL,
    format = "yyyy-mm-dd",
    startview = "day",
    language = "es"
  ),
  selectInput(idRef,
              label="Refrescar datos:",
              choices=c('Activado','En pausa (para análisis)'),
              selected="Activado")
  )
  
}



#CONTROL-----------------

UIControlMonitor <- function() {
  conditionalPanel(
    condition = "input.SideMenu == 'fomTP'",
    column(
      width = 9,
      tagList(
        selectInput (
          'vuelo',
          label = "Número de vuelo:",
          choices = NULL,
          selected = NULL,
          multiple = FALSE
        ),
        selectInput (
          'distMon',
          label = "Distancia:",
          choices = NULL,
          selected = NULL,
          multiple = FALSE
        ),
        selectInput('refresh',
                    label="Refrescar datos:",
                    choices=c('Activado','En pausa (para análisis)'),
                    selected="Activado")
      )
    )
  )
}

UIControlBias <- function() {
  conditionalPanel(
    condition = "input.SideMenu == 'fomTNP'",
    column(
      width = 9,
      tagList(
        selectizeInput (
          'wac',
          label = "Zona WAC de origen:", 
          choices = NULL,
          selected = NULL,
          multiple = FALSE
        ),
        selectizeInput (
          'distBias',
          label = "Distancia:",
          choices = NULL,
          selected = NULL,
          multiple = FALSE
        )
      )
      
    )
  )
}


UIControlInfo <- function () {
  conditionalPanel(
    condition = "input.SideMenu == 'Info'",
    column(
      width = 9)
 
  )
  
}

#BODY--------------

UIBodyMonitor <- function () {
  bs4TabItem(
    tabName = "fomTP",
    fluidRow(
      
      bs4TabCard(
        id = "GrafTabs",
        title = "Desempeño del modelo",
        closable = FALSE,
        width = 12,
        status = NULL,
        solidHeader = FALSE,
        collapsible = TRUE,
        maximizable = TRUE,
        side="right",
        bs4TabPanel(
          tabName= 'Temporal',
          active = TRUE,
          echarts4rOutput("modelos_plot") %>% 
            shinycssloaders::withSpinner(type = 5)#,
          # actionBttn(inputId = "add", 
          #            label = "Actualizar",
          #            #icon = 'paint-brush',
          #            style = 'pill',
          #            size = 'lg',
          #            color = 'primary')
        ),
        bs4TabPanel(
          tabName= 'Distribucional',
          active = FALSE,
          fluidRow( 
            bs4Card( 
            title = paste0("Datos de entrenamiento"),
            closable = FALSE,
            width = 12,
            # height = 400,
            status = 'primary',
            solidHeader = FALSE,
            collapsible = TRUE,
            maximizable = TRUE,
            echarts4rOutput("distribucion_train_plot") %>% 
              shinycssloaders::withSpinner(type = 5)
            )),
          fluidRow(
          bs4Card( 
            title = paste0("Datos de prueba"),
            closable = FALSE,
            width = 12,
            # height = 400,
            status = 'primary',
            solidHeader = FALSE,
            collapsible = TRUE,
            maximizable = TRUE,
            
            echarts4rOutput("distribucion_test_plot") %>% 
                       shinycssloaders::withSpinner(type = 5)
                     )
          
        )
        )
        )
      
      ),
      fluidRow(
      bs4TabCard(
        id = "fomTabs",
        title = "Diagnóstico",
        closable = FALSE,
        width = 12,
        status = NULL,
        solidHeader = FALSE,
        collapsible = TRUE,
        maximizable = TRUE,
        side="right",
        bs4TabPanel(
          tabName= 'Alertas',
          active = TRUE,
          DTOutput("alertas_out") %>% shinycssloaders::withSpinner(type = 5)
        ),
        bs4TabPanel(
          tabName= 'Datos',
          active = FALSE,
          DTOutput("modelos_out") %>% shinycssloaders::withSpinner(type = 5)
        )
      )
    )
  )
}


UIBodyBias <- function () {
  bs4TabItem(
    tabName = "fomTNP",
    fluidRow(bs4TabCard(
      id = "fomTabs",
      title = "Fairness & Bias",
      closable = FALSE,
      width = 12,
      status = NULL,
      solidHeader = FALSE,
      collapsible = TRUE,
      maximizable = TRUE,
      side="right",
      bs4TabPanel(
        tabName= 'Matriz de confusión',
        active = FALSE,
        echarts4rOutput('confmat_plot') %>% 
          shinycssloaders::withSpinner(type=5)
        
      ),
      bs4TabPanel(
        tabName= 'Barras',
        active = TRUE,
        echarts4rOutput('barras_plot') %>% 
          shinycssloaders::withSpinner(type=5)
      )
    )
    ),
    fluidRow(
      
      bs4Card( 
        title = paste0("Diagnóstico del Fairness & Bias"),
        closable = FALSE,
        width = 12,
        # height = 400,
        status = 'primary',
        solidHeader = FALSE,
        collapsible = TRUE,
        maximizable = TRUE,
        DTOutput("fb_out") %>% shinycssloaders::withSpinner(type = 5)
      )
    )
  )
}

UIBodyInfo<- function () {
 
  bs4TabItem(
    tabName = "Info",
    fluidRow(
      bs4TabCard(
        id = "info",
        title = paste0("Definición del Monitoreo"),
        closable = FALSE,
        width = 12,
        status = NULL,
        solidHeader = FALSE,
        collapsible = TRUE,
        maximizable = TRUE,
        side="right",
        bs4TabPanel(
          tabName= 'Modelo Ganador',
          active = TRUE,
            DTOutput("info3") %>% 
              shinycssloaders::withSpinner(type = 5))
        
      )
    )
  )
   
}
