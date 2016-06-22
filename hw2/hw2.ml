type ('nonterminal, 'terminal) symbol =
    | N of 'nonterminal
    | T of 'terminal
;;

let rec gimme_rules rules nonterminal =
	match rules with
	| [] -> []
	| (start, rhs)::rest -> if start = nonterminal 
							then rhs::gimme_rules rest nonterminal
							else gimme_rules rest nonterminal

let convert_grammar gram =
	match gram with
	| start, rules -> (start, gimme_rules rules)

(* alt_list: list of rhs for a nonterminal symbol *)

let rec match_rhs prod_fxn rhs accept derivation frag =
	match rhs with
	| [] -> accept derivation frag
	| _ -> match frag with
		| [] -> None
		| terminal::terminals -> match rhs with
			| (N x)::symbols -> (make_or_matcher x prod_fxn (prod_fxn x) (match_rhs prod_fxn symbols accept) derivation frag)
			| (T x)::symbols -> 
				if x = terminal 
				then (match_rhs prod_fxn symbols accept derivation terminals)
				else None

and make_or_matcher start prod_fxn alt_list accept derivation frag =
	match alt_list with
	| [] -> None
	| rhs::rest -> 
		match (match_rhs prod_fxn rhs accept (derivation@[start, rhs]) frag) with
		| None -> (make_or_matcher start prod_fxn rest accept derivation frag)
		| ok -> ok

let parse_prefix (start, prod_fxn) accept frag =
	make_or_matcher start prod_fxn (prod_fxn start) accept [] frag 







