from string import ascii_letters, digits, punctuation


DEFAULT_FONT = "Microsoft Sans Serif"

GLYPHS_V1 = " 0hr123456789-+JanuyFebMcApilgstSmOoNvDBCEdqVjxGHILPRTU" 

diacritics = "áćéíĺḿńóṕŕśúýźàèìòùỳẁâĉêĝĥîĵôŝûŵŷăčďěğǐǰǩľňǒřšťǔžőűäëïöüÿãẽĩñõũỹçȩşţāēīōūȳæœþø"
GLYPHS_V2 = digits + ascii_letters + punctuation + diacritics + diacritics.upper() + " -+"
