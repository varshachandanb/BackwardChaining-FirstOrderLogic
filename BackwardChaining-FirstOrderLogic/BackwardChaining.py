import re
import sys


def standardize_var(pred,i):
    left, bracket, rest = pred.partition("(")
    block, bracket, right = rest.partition(")")
    if(len(block)==1):
        new_block=block+str(i)
        new_sentence = left + "(" + block.replace(block,new_block) + ")" + right
    else:
        new_block=""
        bl=block.split(',')
        for x in range(len(bl)):
            if(bl[x].islower()):
                bl[x]=bl[x]+str(i)
            new_block+=bl[x]
        new_block=re.sub(" ",", ",new_block)
        new_sentence = left + "(" + block.replace(block,new_block) + ")" + right
    return new_sentence

def fol_bc_ask_or(know_base,query):
    theta = {}
    #full kb, v(x) && t(x,y,z) && a(x), {}
    res = fol_bc_or(know_base, query, theta)
    for se in res:
        if -1 in se: continue
        elif fol_entails(se):
            #otpt.write("True"+'\n')
            return TRUE
    #otpt.write("False"+'\n')
    return FALSE



def fol_entails(se):
    return True if TRUE in se and -1 not in se else False

#t(x0),t(A),{}
# x0,A,{}
def unify(x,y,t):
    if(-1 in t):
        return t
    elif (x==y):
        return t
    elif x.islower() and ',' not in x and '('  not in x:
        unify_var(x,y,t)
    elif y.islower() and ',' not in y and '(' not in y:
        unify_var(y,x,t)
        #T(x) T(A)
    elif '(' in x and '(' in y:
        #t(x0),t(A),{} => x0,A,{}
        t=unify(x.split("(", 1)[0], y.split("(", 1)[0], t)
        return unify(get_args(x),get_args(y),t)
        #A,x,S   A,P,z
    elif ',' in x and ',' in y:
        if '(' in x:
            first_x,rest_x=find_ft_rt_1(x)
        else:
            first_x,rest_x=find_ft_rt_2(x)
        if ')' in y:
            first_y,rest_y=find_ft_rt_1(y)
        else:
            first_y,rest_y=find_ft_rt_2(y)
        unify(first_x,first_y,t)
        return unify(rest_x,rest_y,t)
    else:
        t[-1]=-1
        return t

def unify_var(var,x,t):
    if var in t:
        return unify(t[var], x, t)
    if x in t:
        return unify(t[x], x, t)
    if occur_check(var, x, t):
        t[-1] = -1
        return t
    else:
        #Anakin: x0
        t[var] = x

#if(Anakin in t : check all possible substitution for Anakin=> A,x,t)
def occur_check(var,x,t):
    if var == x:
        return True
    elif x.islower() and ',' not in x and '(' not in x and x in t:
        return occur_check(var, t[x], t)
    elif '(' in x:
        if ',' in x:
            return occur_check(var, get_args(x),t)
        else:
            return occur_check(var, x.split("(", 1)[0],t)
    else:
        return False


def get_args(term):
    if "(" in term:
        t1 = term.split("(", 1)[1]
        return t1[:len(t1)-1]


def find_ft_rt_1(x):
    x_first = x[0:x.find(')')+1]
    x_rest = x[x.find(')') + 2:len(x)]
    return (x_first.strip(), x_rest.strip())


def find_ft_rt_2(x):
    x_first = x.split(",", 1)[0]
    x_rest = x.split(",", 1)[1]
    return (x_first.strip(), x_rest.strip())

def subs_values(ft,t):
    term = ""
    if ',' in get_args(ft):
        arg=get_args(ft).split(',')
        for m in range(len(arg)):
            if(arg[m].strip() not in t):
                if(arg[m].islower()):
                    term=term+" _"+','
                else:
                    term=term+arg[m]+','
            if arg[m].strip() in t :
                if t[arg[m].strip()].islower():
                    term=term+" _"+','
                else:
                    term = term +" "+t[arg[m].strip()] + ','
    else:
        arg=get_args(ft)
        if(arg not in t):
            if(arg.islower()):
                term=term+" _"+','
            else:
                term=term+arg+','
        if arg in t :
            if t[arg].islower():
                term=term+" _"+','
            else:
                term = term + " "+t[arg] + ','

    term = term.strip(',')
    term=term.strip()
    #V(x)=> V( + Anakin +)=>V(Anakin)
    temp_ft = ft.split("(", 1)[0] + '(' + term + ')'
    return temp_ft

def fol_bc_and(know_base,target,t):
    global target_printed
    if(t):
        if -1 in t:
            return t
    if(len(t)==0):
        return t
    ft=target
    rt=""
    if("&&" in target):
        ft=target.split("&&",1)[0]
        rt=target.split("&&",1)[1]
        ft=ft.strip()
        rt=rt.strip()
    for j in t:
        if '_' not in t[j]:
            complete_theta[j]=t[j]
    for k in complete_theta:
        if(complete_theta[k] in complete_theta):
            complete_theta[k]=complete_theta[complete_theta[k]]

    temp_ft=subs_values(ft,complete_theta)

    otpt.write("Ask: "+temp_ft+'\n')
    arg=get_args(ft).split(',')
    for ar in arg:
        if '(' not in ar and '_' not in ar:
            if ar.islower() and ',' not in ar and '(' not in ar:
                #x0 in subst dictionary
                if ar in complete_theta:
                    #t[x0]=>Anakin
                    subs = complete_theta[ar]
                    if subs.islower() and ',' not in subs and '(' not in subs and subs in complete_theta and '_' not in subs:
                        subs = complete_theta[subs]
                    #x,y,z
                    for m in arg:
                        if m.strip() == ar.strip():
                            #arg[0] was x now it is arg[0]=> Anakin
                            arg[arg.index(m.strip())] = subs
                term = ""
                for ar in arg:
                    if ar.strip() in complete_theta and "_" not in ar:
                        term = term +" "+complete_theta[ar.strip()] + ','
                    elif '_' not in ar:
                        term = term +" "+ar.strip() + ','
                term = term.strip(',')
                term=term.strip()
                ft = ft.split("(", 1)[0] + '(' + term + ')'
    rt_part = fol_bc_or(know_base, ft, complete_theta)
    check = True
    for li in rt_part:
        if rt and -1 not in li:
            fol_bc_and(know_base, rt, li)
        if -1 not in li and TRUE in li:
            t.update(li)
            check = False
    if check:
        t[-1] = -1
    return t


def fol_bc_or(know_base,target,theta):
    #T(x)
    or_count=0
    max_or_count=0
    global true_count
    u_lst = list()
    present=False
    if target in know_base and TRUE in know_base[target]:
        theta[TRUE] = TRUE
        otpt.write("True: "+target+'\n')
        true_count=1
        for m in theta:
            if m not in complete_theta:
                complete_theta[m]=theta[m]
        for k in complete_theta:
            if(complete_theta[k] in complete_theta):
                complete_theta[k]=complete_theta[complete_theta[k]]
        if -1 in theta:
            del theta[-1]
        u_lst = u_lst + [theta]
        return u_lst

    for key in know_base:
        if key.split("(", 1)[0] == target.split("(", 1)[0]:
            max_or_count=max_or_count+1
    true_count=0
    for key in range(len(kb_keys)):
        if kb_keys[key].split("(", 1)[0] == target.split("(", 1)[0] and true_count==0:
            or_count=or_count+1
            present = True
            for value in know_base[kb_keys[key]]:
                thet={}
                if value != TRUE:
                    #t(x0), t(A),{}
                    unify(kb_keys[key], target, thet)
                    fol_bc_and(know_base, value, thet)
                    if(or_count<max_or_count and TRUE not in thet):
                        tmp_target=subs_values(target,complete_theta)
                        otpt.write("Ask: "+ tmp_target+'\n')
                else:
                    #Viterbi(Anakin)=true
                    unify(kb_keys[key], target, thet)
                    if(-1 not in thet):
                        thet[TRUE]=TRUE
                    #fol_bc_and(know_base, target, thet)
            if TRUE in thet and -1 not in thet:
                thet = dict(thet.items()+theta.items())
                if -1 in thet:
                    del thet[-1]
                u_lst = u_lst + [thet]
                for j in thet:
                    if j not in complete_theta:
                        complete_theta[j]=thet[j]
                for k in theta:
                    if theta[k] in thet:
                        complete_theta[k]=thet[theta[k]]
                target=subs_values(target,complete_theta)
                otpt.write("True: "+ target+'\n')
                true_count=1

    if not present or not u_lst:
        theta[-1] = -1
        u_lst = u_lst + [theta]
        target=subs_values(target,complete_theta)
        otpt.write("False: "+ target+'\n')
    return u_lst


if __name__ == '__main__':
    kb=[]
    kb_keys={}
    tmp_know_base={}
    know_base={}
    TRUE = 'True'
    FALSE = 'False'
    final_result="True"
    target_printed=False
    true_count=0
    complete_theta={}
    #inpt=open(sys.argv[-1])
    inpt=open("input.txt","r")
    lines=inpt.readlines()
    goal=lines[0].rstrip('\n')
    no_q=lines[1].rstrip('\n')
    for m in range(2,int(no_q)+2):
        kb.append(lines[m].rstrip('\n'))
    inpt.close()
    for x in range(len(kb)):
        if("=>" in kb[x]):
            predicates=kb[x].split("=>")
            predicates[1]=predicates[1].strip()
            predicates[1]=standardize_var(predicates[1],x)
            split_pred = predicates[0].split('&&')
            for y in range(len(split_pred)):
                split_pred[y] = standardize_var(split_pred[y], x)
            predicates[0] = '&&'.join(split_pred)
            kb[x] = predicates[0]+"=>"+predicates[1]
        if "=>" in kb[x]:
            lst = kb[x].split("=>")
            kb_keys[x]=lst[1].strip()
            if lst[1] in know_base:
                # 2 or more sentence yield the same target or condition
                know_base[lst[1]].append(lst[0].strip())
            else:
                # only one condition in or statement
                know_base[lst[1]] = [lst[0].strip()]
        else:
            kb_keys[x]=kb[x].strip()
            know_base[kb[x]] = [TRUE]
    otpt=open("output.txt","w")
    tmp_goal=goal
    first=goal
    rest=""
    if("&&" in goal):
        pred=goal.split("&&")
        if(len(pred)>1):
            for i in range (len(pred)-1):
                first=tmp_goal.split("&&",1)[0]
                rest=tmp_goal.split("&&",1)[1]
                first=first.strip()
                rest=rest.strip()
                tmp_goal=subs_values(first,complete_theta)
                otpt.write("Ask: "+tmp_goal+'\n')
                result=fol_bc_ask_or(know_base,first)
                if("False" in result):
                    final_result="False"
                tmp_goal=rest
            first=tmp_goal.split("&&",1)[0]
            first=first.strip()
            tmp_goal=subs_values(first,complete_theta)
            otpt.write("Ask: "+tmp_goal+'\n')
            tmp_result=fol_bc_ask_or(know_base,first)
            if("False" in final_result):
                otpt.write(final_result)
            else:
                otpt.write(tmp_result)
            print result
    else:
        tmp_goal=subs_values(tmp_goal,complete_theta)
        otpt.write("Ask: "+tmp_goal+'\n')
        result=fol_bc_ask_or(know_base,goal)
        otpt.write(result)
        print result
    #print ub
    otpt.close()


