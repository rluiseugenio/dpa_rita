bs4DashPage(
  enable_preloader = TRUE,
  navbar = bs4DashNavbar(
    controlbarIcon = "filter",
    rightUi = bs4DropdownMenu(
      show = FALSE,
      status = "info",
      menuIcon = "info-circle",
      bs4DropdownMenuItem(
        message =  paste0("Datos al: "),
        time = today(),
        icon = NULL
      ),
      bs4DropdownMenuItem(
        message =  paste0("Version 1.0"),
        time = "2020-05-15",
        icon = NULL
      )
    )
  ),
  tags$head(HTML("<link href='http://fonts.googleapis.com/css?family=Roboto' rel='stylesheet' type = 'text/css'>")),
  tags$head(tags$style(
    HTML(
      "
           #PivotBox{
           overflow-y: scroll;
           overflow-x: scroll;
           height:600px;
           }
          
          div.dataTables_length {
            margin-right: 15em;
            margin-bottom: 1em;
          }
           * { font-family: Roboto; }
          
          label.control-label {
          padding-right: 5px;
                  
          }
                  
          .selectize-control.single div.item {
            padding-right: 10px;
          }
                  
          .selectize-dropdown {
            width: 470px !important;
          }
                  
          .section.sidebar .shiny-input-container {
            padding-top:0px;
            padding-bottom:0px;
          }
                  
          .shiny-date-input{
            z-index:99999 !important;
          }
          
          .info-box-icon {
            border-radius: .25rem;
            display: block;
            width: 110px;
            text-align: center;
            font-size: 50px;
         }
           "
    )
  )),
  
  sidebar =  bs4DashSidebar(
    skin = "dark",
    status = "primary",
    title = "Monitoreo",
    brandColor = "primary",
    src = "https://seeklogo.com/images/I/IATA-logo-3CE0FA8A11-seeklogo.com.png",
    elevation = 3,
    opacity = 0.8,
    bs4SidebarMenu(
      id = "SideMenu",
      tabName = "Monitoreo",
      icon = "tachometer-alt",
      startExpanded = TRUE,
      selected = TRUE,

      bs4SidebarMenuSubItem(
        text = "Modelos",
        tabName = "fomTP",
        icon = "angle-double-left"
      ),
      bs4SidebarMenuSubItem(
        text = "Fairness & Bias",
        tabName = "fomTNP",
        icon = "angle-double-right"
      ),
     bs4SidebarMenuSubItem(
        "Información",
        tabName = "Info",
        icon = "handshake"
      )
      
    )
    
  ),
  controlbar = bs4DashControlbar(
    UIControlMonitor(),
    UIControlBias(),
    UIControlInfo()
  ),
  body = bs4DashBody(
    bs4TabItems(
        UIBodyMonitor(),
        UIBodyBias(),
        UIBodyInfo()
    )
  )
)





