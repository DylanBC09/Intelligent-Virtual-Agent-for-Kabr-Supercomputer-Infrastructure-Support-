extract.records <- function(line) {
  
  values.part <- sub("^INSERT INTO `[^`]+` VALUES ", "", line)
  values.part <- sub(";$", "", values.part)
  
  chars <- strsplit(values.part, "")[[1]]
  
  records <- c()
  current <- ""
  
  depth <- 0
  in.string <- FALSE
  escaped <- FALSE
  
  for (ch in chars) {
    
    if (escaped) {
      current <- paste0(current, ch)
      escaped <- FALSE
      next
    }
    
    if (ch == "\\") {
      current <- paste0(current, ch)
      escaped <- TRUE
      next
    }
    
    if (ch == "'") {
      in.string <- !in.string
      current <- paste0(current, ch)
      next
    }
    
    if (!in.string && ch == "(") {
      depth <- depth + 1
    }
    
    if (!in.string && depth == 0 && ch == ",") {
      next
    }
    
    current <- paste0(current, ch)
    
    if (!in.string && ch == ")") {
      
      depth <- depth - 1
      
      if (depth == 0) {
        rec <- sub("^\\(", "", current)
        rec <- sub("\\)$", "", rec)
        records <- c(records, rec)
        current <- ""
      }
    }
  }
  
  records
}

parse.record <- function(x) {
  
  chars <- strsplit(x, "")[[1]]
  
  fields <- c()
  current <- ""
  
  in.string <- FALSE
  escaped <- FALSE
  
  for (ch in chars) {
    
    if (escaped) {
      current <- paste0(current, ch)
      escaped <- FALSE
      next
    }
    
    if (ch == "\\") {
      escaped <- TRUE
      current <- paste0(current, ch)
      next
    }
    
    if (ch == "'") {
      in.string <- !in.string
      current <- paste0(current, ch)
      next
    }
    
    if (ch == "," && !in.string) {
      fields <- c(fields, current)
      current <- ""
    } else {
      current <- paste0(current, ch)
    }
  }
  
  c(fields, current)
}

classify_ticket_optimized <- function(text) {
  tokens <- get_ngrams(text)
  human_score <- sum(tokens %in% human_admin_patterns)
  env_score   <- sum(tokens %in% iva_env_patterns)
  cmd_score   <- sum(tokens %in% iva_cmd_patterns)
  
  if (human_score > 0) {
    return(list(category = "HUMAN", subtype = "HUMAN"))
  } else if (env_score >= cmd_score && env_score > 0) {
    return(list(category = "IVA", subtype = "IVA_ENVIRONMENT"))
  } else {
    return(list(category = "IVA", subtype = "IVA_COMMANDS"))
  }
}
