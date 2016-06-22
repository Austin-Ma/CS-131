(* warm up *)

let rec subset a b =
if a == [] then true
else ((List.mem (List.hd a) b) && subset (List.tl a) b);;

let equal_sets a b =
(subset a b) && (subset b a);;

let rec set_union a b = match a with
    | [] -> b
    | head::tail -> if List.mem head b then set_union tail b
                    else head::set_union tail b;;

let rec set_intersection a b = match a with
    | [] -> []
    | head::tail -> if List.mem head b then head::set_intersection tail b
                    else set_intersection tail b;;

let rec set_diff a b = match a with
    | [] -> []
    | head::tail -> if List.mem head b then set_diff tail b
                    else head::set_diff tail b;;

let rec computed_fixed_point eq f x =
if eq x (f x) then x
else computed_fixed_point eq f (f x);;

let apply_function f g = fun x -> f (g x);;

let rec repeat_function f n =
if n == 1 then f
else apply_function f (repeat_function f (n-1));;

let rec computed_periodic_point eq f p x =
if p == 0 then x
else if eq x (repeat_function f p x) then x
else computed_periodic_point eq f p (f x);;

(* real work *)

type ('nonterminal, 'terminal) symbol =
    | N of 'nonterminal
    | T of 'terminal
;;

let equal_rules a b =
equal_sets (snd a) (snd b)
;;

let is_symbol_terminal good_nonterminal_symbols = function
    | T symbol -> true
    | N symbol -> subset [symbol] good_nonterminal_symbols
;;

let rec is_rhs_good rhs good_nonterminal_symbols = match rhs with
    | [] -> true
    | symbol::rest -> if is_symbol_terminal good_nonterminal_symbols symbol
        then is_rhs_good rest good_nonterminal_symbols
        else false
;;

let rec filter_rules rules good_symbols = match rules with
| [] -> good_symbols
| rule::rest -> if (is_rhs_good (snd rule) good_symbols) && not (subset [(fst rule)] good_symbols)
    then filter_rules rest ((fst rule)::good_symbols)
    else filter_rules rest good_symbols
;;

let get_filtered_rules (rules, good_symbols) =
(rules, filter_rules rules good_symbols)
;;

let get_good_symbols rules =
snd (computed_fixed_point equal_rules get_filtered_rules (rules, []))
;;

let rec get_ordered_filtered_rules rules good_symbols = match rules with
    | [] -> []
    | rule::rest -> if is_rhs_good (snd rule) good_symbols
        then rule::get_ordered_filtered_rules rest good_symbols
        else get_ordered_filtered_rules rest good_symbols
;;

let filter_blind_alleys g = match g with
    | (start, rules) -> (start, get_ordered_filtered_rules rules (get_good_symbols rules))
;;






