type id = string

exception NotImplemented

type k  = KArrow of id * k * k
           | KType
           | KSingleton of c 
and c = TyVar of id
           | TyFn of id * c
           | TyAp of c * c
           | Ty1
           | TyProd of c * c
           | TySum of c * c

exception BadBinding

let rec subst c (* for *) id c' = 
  match c' with
  | TyVar id' -> 
      if id == id' then 
        c
      else 
        c'
  | TyFn (id', body) -> 
      if id == id' then 
        raise BadBinding
      else
        TyFn(id', (subst c id body))
  | TyAp (c1, c2) -> 
      TyAp ((subst c id c1),
            (subst c id c2))
  | Ty1 -> Ty1
  | TyProd (c1, c2) -> 
      TyProd ((subst c id c1),
              (subst c id c2))
  | TySum (c1, c2) ->
      TySum ((subst c id c1),
             (subst c id c2))

let rec ksubst c (* for *) id k = 
  match k with 
  | KArrow (id', k1, k2) -> 
      if id == id' then 
        raise BadBinding
      else
        KArrow (id', (ksubst c id k1), (ksubst c id k2))
  | KType -> KType
  | KSingleton c' -> KSingleton (subst c id c')

type ctx = (c * c * k) list

let rec lookup ctx c = 
  match ctx with 
  | [] -> None
  | (c', v, k) :: ctx' -> 
      if c == c' then 
        Some (v, k)
      else
        lookup ctx' c

exception IllKinded
let rec ceval ctx c = 
  match lookup ctx c with 
  | Some (v, _) -> (v, ctx)
  | None -> begin match c with 
    | _ -> raise NotImplemented
    end
let rec ceq (ctx) (c1) (c2) (k) : bool = 
  if c1 == c2 then
    let k1 = syn_kind ctx c1 in 
    let k2 = syn_kind ctx c2 in 
    keq ctx k1 k2
  else 
    let (v1, ctx') = ceval ctx c1 in 
    let (v2, ctx'') = ceval ctx' c2 in 
    match (v1, v2) with 
    | TyVar id1, TyVar id2 -> raise NotImplemented
    | _ -> raise NotImplemented
and keq (ctx) (k1) (k2) : bool = 
  if k1 == k2 then true else
    match (k1, k2) with 
    | (KArrow (id1, k11, k12), KArrow(id2, k21, k22)) -> 
        let k22' = ksubst (TyVar id1) id2 k22 in 
        keq ctx k11 k21 && keq ctx k12 k22'
    | (KArrow _, _) -> false
    | (_, KArrow _) -> false
    | (KSingleton c1, KSingleton c2) -> ceq ctx c1 c2 KType
    | _ -> false
and ksub k1 k2 = raise NotImplemented 
and syn_kind (ctx : ctx) (c) : k = 
  match lookup ctx c with 
  | Some (_, k) -> k
  | None -> begin match c with 
    | TyVar _ -> raise IllKinded
    | TyFn (id, body) -> 
        let ctx' = (TyVar id, TyVar id, KType) :: ctx in 
        syn_kind ctx' body
    | TyAp (c1, c2) -> 
        begin match syn_kind ctx c1 with   
        | KArrow (id, k, k') -> 
            let k2 = syn_kind ctx c2 in 
              if keq ctx k k2 then 
                ksubst c2 id k'
              else
                raise IllKinded
        | _ -> raise IllKinded
        end
    | Ty1 -> KType
    | TyProd (c1, c2) -> 
        let k1 = syn_kind ctx c1 in 
        let k2 = syn_kind ctx c2 in 
        if ksub k1 KType && ksub k2 KType then 
          KType
        else
          raise IllKinded
    | TySum (c1, c2) -> 
        let k1 = syn_kind ctx c1 in 
        let k2 = syn_kind ctx c2 in 
        if ksub k1 KType && ksub k2 KType then 
          KType
        else
          raise IllKinded
 end
