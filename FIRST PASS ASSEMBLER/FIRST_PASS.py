import sys
import csv
import re
import os

def formatting():
    filename="linear_search.asm"
    global out
    f=open(filename)
    w=open("symbol.txt",'w')
    out="NAME\tOFFSET\tSIZE\tTYPE\tSEGMENT\n"
    
    for line in f:
        words=line.strip().split(" ")
        for i in range(len(words)):
            if words[i]==' ':
                words[i:]=words[i+1:]
            elif words[i]==':':
                words[i-1]+=':'
                words[i:]=words[i+1:]
                
        if 'END' in line.upper():
            pass

        if words!=[]:
            evaluate(words)
    w.write(out)    

def opcodes(word):
    opcode=['CMP','JZ','INC','LOOP','JA','JB','ADD','SUB','SHR','SHL','XCHG','LDS','LEA']
    size=[2,2,1,2,2,2,2,2,1,1,2,4,4]
    for i in range(len(opcode)):
        if word.upper()==opcode[i]:
            return size[i]
        
    return -1

def size_directive(word):
    directive=['DB','DW','DD']
    size=[1,2,4]
    for i in range(len(directive)):
        if word.upper()==directive[i]:
            return size[i]
    return -1

def MOV(string):
        '''
        pat1 -REGISTER ADD MODE -              AX,BH
        PAT2- IMMEDIATE ADD MODE -             110029,528,100H,'AB',XX-YX+5
        PAT3- DIRECT ADD MODE -                WGT,ARRAY+5,CNT-5
        PAT4- REG INDIRECT ADD MODE -          [BX]
        PAT5- REG RELATIVE ADD MODE-           VAR[BX],[BX-5],VAR[BX-5]
        PAT6- BASE INDEX ADD MODE -            [BX][SI]
        PAT7- RELATIVE BASE INDEX ADD MODE -   VAR[BX][SI],VAR[BX+5][SI-5],[BX+5][SI-5]

        pat_rev = It is the vice-versa of the instruction for eg-  if instr is:
                 "MOV AX,[1234H]" then rev becomes "MOV [1234H],AX"
                 THIS WORKS ON ALL MODES EXCEPT IMMEDIATE ADD MODE.
                 
        '''

        pat1='(^MOV[\s]+(AX|AL|AH|BX|BL|BH|CX|CL|CH|DX|DL|DH|SI|DI|BP|SP|DS|ES)[\s]*,[\s]*((AX|BX|CX|DX|SI|DI|BP|SP|DS|ES))[\s]*$)'
        pat2='(^MOV[\s]+((AX|AL|AH|BX|BL|BH|CX|CL|CH|DX|DL|DH|SI|DI|BP|SP|DS|ES)|([a-z]+))[\s]*,[\s]*[0-9]+(H|B|D|O){0,1}[\s]*$)'
        
        pat3='(^MOV[\s]+(AX|AL|AH|BX|BL|BH|CX|CL|CH|DX|DL|DH|SI|DI|BP|SP|DS|ES)[\s]*,[\s]*(([\[0-9\]]+)|([a-z]+\+[0-9]*H{0,1})|([0-9]*H{0,1}\+[a-z]+)|([a-zA-Z]+))[\s]*$)'
        pat3_rev='(^MOV (([\[0-9\]]+)|([a-z]+\+[0-9]*H{0,1})|([0-9]*H{0,1}\+[a-z]+)|([a-zA-Z]+)),(AX|AL|AH|BX|BL|BH|CX|CL|CH|DX|DL|DH|SI|DI|BP|SP|DS|ES)$)'

        pat4='(^MOV[\s]+(AX|AL|AH|BX|BL|BH|CX|CL|CH|DX|DL|DH|SI|DI|BP|SP|DS|ES)[\s]*,[\s]*(\[(AX|BX|CX|DX|SI|DI)\])[\s]*$)'
        pat4_rev='(^MOV (\[(AX|BX|CX|DX|SI|DI)\])[\s]*,[\s]*(AX|AL|AH|BX|BL|BH|CX|CL|CH|DX|DL|DH|SI|DI|BP|SP|DS|ES)[\s]*$)'

        pat5='(^MOV[\s]+(AX|AL|AH|BX|BL|BH|CX|CL|CH|DX|DL|DH|SI|DI|BP|SP|DS|ES)[\s]*,[\s]*((\[(AX|BX|CX|DX|SI|DI|DS|ES)\+[0-9]+H{0,1}\])|(\[(AX|BX|CX|DX|SI|DI|DS|ES)\+[a-z A-Z]+\])|([A-Z]+\[(AX|BX|CX|DX|SI|DI|DS|ES)\])|([A-Z]+\+(AX|BX|CX|DX|SI|DI|BP|SP|DS|ES))|([0-9]+H{0,1}\[(AX|BX|CX|DX|SI|DI|BP|SP|DS|ES)\]))[\s]*$)'
        pat5_rev='(^MOV ((\[(AX|BX|CX|DX|SI|DI|DS|ES)\+[0-9]+H{0,1}\])|(\[(AX|BX|CX|DX|SI|DI|DS|ES)\+[a-z A-Z]+\])|([A-Z]+\[(AX|BX|CX|DX|SI|DI|DS|ES)\])|([A-Z]+\+(AX|BX|CX|DX|SI|DI|BP|SP|DS|ES))),(AX|AL|AH|BX|BL|BH|CX|CL|CH|DX|DL|DH|SI|DI|BP|SP|DS|ES)$)'

        pat6='(^MOV[\s]+(AX|AL|AH|BX|BL|BH|CX|CL|CH|DX|DL|DH|SI|DI|BP|SP|DS|ES)[\s]*,[\s]*(((AX|BX|CX|DX|BP|DS|ES)\[(SI|DI)\])|((AX|BX|CX|DX|BP|DS|ES)\+(SI|DI))|(\[(AX|BX|CX|DX|BP|DS|ES|SI|DI)\+(AX|BX|CX|DX|BP|DS|ES|SI|DI)\]))[\s]*$)'
        pat6_rev='(^MOV (((AX|BX|CX|DX|BP|DS|ES)\[(SI|DI)\])|((AX|BX|CX|DX|BP|DS|ES)\+(SI|DI))|(\[(AX|BX|CX|DX|BP|DS|ES|SI|DI)\+(AX|BX|CX|DX|BP|DS|ES|SI|DI)\])),(AX|AL|AH|BX|BL|BH|CX|CL|CH|DX|DL|DH|SI|DI|BP|SP|DS|ES)$)'
        
        pat7='(^MOV[\s]+(AX|AL|AH|BX|BL|BH|CX|CL|CH|DX|DL|DH|SI|DI|BP|SP|DS|ES)[\s]*,[\s]*(((AX|BX|CX|DX|BP|DS|ES)\[(SI|DI)\+[0-9]+H{0,1}\])|((AX|BX|CX|DX|BP|DS|ES)\+(SI|DI)\+[0-9]+H{0,1})|([a-zA-Z]*\[(AX|BX|CX|DX|BP|DS|ES|SI|DI)\]\[(AX|BX|CX|DX|BP|DS|ES|SI|DI)\]))[\s]*$)'
        pat7_rev='(^MOV (((AX|BX|CX|DX|BP|DS|ES)\[(SI|DI)\+[0-9]+H{0,1}\])|((AX|BX|CX|DX|BP|DS|ES)\+(SI|DI)\+[0-9]+H{0,1})|([a-zA-Z]*\[(AX|BX|CX|DX|BP|DS|ES|SI|DI)\]\[(AX|BX|CX|DX|BP|DS|ES|SI|DI)\]))[\s]*,[\s]*(AX|AL|AH|BX|BL|BH|CX|CL|CH|DX|DL|DH|SI|DI|BP|SP|DS|ES)$)'
        

        
        match=re.search(pat1,string,re.IGNORECASE)
        if match:
            #print("REGISTER Addressing mode")  
            #print(match.group())
            return 2
            
        match=re.search(pat2,string,re.IGNORECASE)
        if match:
            #print("IMMEDIATE Addressing mode")   
            #print(match.group())
            return 4
            
        match=re.search(pat3,string,re.IGNORECASE)
        if match:
            #print("DIRECT Addressing mode")
            #print(match.group())
            return 2
            

        match=re.search(pat3_rev,string,re.IGNORECASE)
        if match:
            #print("DIRECT Addressing mode")
            #print(match.group())
            return 2
            
        match=re.search(pat4,string,re.IGNORECASE)
        if match:
            #print("REGISTER INDIRECT Addressing mode")
            #print(match.group())
            return 2
            
        match=re.search(pat4_rev,string,re.IGNORECASE)
        if match:
            #print("REGISTER INDIRECT Addressing mode")
            #print(match.group())
            return 2
            

        match=re.search(pat6,string,re.IGNORECASE)
        if match:
            #print("BASE INDEX Addressing mode")
            #print(match.group())
            return 4
            
        match=re.search(pat6_rev,string,re.IGNORECASE)
        if match:
            #print("BASE INDEX Addressing mode")
            #print(match.group())
            return 4
            
        match=re.search(pat5,string,re.IGNORECASE)
        if match:
            #print("REGISTER RELATIVE Addressing mode")
            #print(match.group())
            return 4

        match=re.search(pat5_rev,string,re.IGNORECASE)
        if match:
            #print("REGISTER RELATIVE Addressing mode")
            #print(match.group())
            return 4
            
        match=re.search(pat7,string,re.IGNORECASE)
        if match:
            #print("RELATIVE BASE INDEXED Addressing mode")
            #print(match.group())
            return 5
               
        match=re.search(pat7_rev,string,re.IGNORECASE)
        if match:
            #print("RELATIVE BASE INDEXED Addressing mode")
            #print(match.group())
            return 4
               

def evaluate(line):
    global lctr,sgctr,curseg,directive,out
    directive=1
    
    if line==[]: return

    if line[0]=='':return
        
    #COMMENT
    if line[0][0]==";":
        return


    #WHEN ORG DIRECTIVE IS GIVEN
    if line[0].upper()=="ORG":
        if line[1][-1].upper()=="H":                                                             
            lctr=int(line[1][:-1],16)
        else:
            lctr=int(line[1])


    #DATA SEGMENT,CODE SEGMENT etc :
    if len(line)>1 and line[1].upper()=="SEGMENT":
        curseg=line[0].upper()
        lctr=0
        out+=curseg+'\t'+str(format(int(sgctr),'05x'))+"\t-5\tSEGMENT\tITSELF\n"
        #w.write(out,delimiter='\n')
        print(curseg+'\t'+str(format(int(sgctr),'05x'))+"\t-5\tSEGMENT\tITSELF")
        sgctr+=1
        return


    #CODE ENDS
    if len(line)>1 and line[1].upper()=="ENDS":
        return


    #END START
    if len(line)>1 and line[0].lower()=="end":
        return


    #FOR -LABEL- LIKE "START:" & NOT INCLUDING ASSUME AS IT IS A DIRECTIVE 
    if line[0][-1]==":":
        if line[0][:-1].upper()=="ASSUME":
            return
            
        out+=(line[0][:-1].upper()+'\t'+str(format(int(lctr),'05x'))+"\t-1\tLABEL\tCODE\n")
        print(line[0][:-1].upper()+'\t'+str(format(int(lctr),'05x'))+"\t-1\tLABEL\tCODE")
        evaluate(line[1:])
        return


    #ALL THE DECLARATION OF -IDENTIFIERS- FOR eg- "ARR DB 1,2,3,4" OR "ARR DB 5 DUP(?)"
    if len(line)>directive :
        size_dir=size_directive(line[directive].upper())
        if size_dir!=-1:

            out+=(line[directive-1].upper()+"\t"+str(format(lctr,'05x'))+"\t"+str(size_dir)+"\tVAR\t"+str(curseg)+"\n")
            print(line[directive-1].upper(),"\t",format(lctr,'05x'),"\t",size_dir,"\tVAR\t",curseg)
            
            if len(line)>3 and line[directive+2][:3].lower()=="dup":
                numofele=int(line[directive+1])
            else:numofele=len(line[directive+1].split(','))

            lctr+=size_dir*numofele
            return


    #IF IT IS A MACHINE INSTRUCTION FOR EG- MOV,CMP,JMP ETC
    opcde=opcodes(line[0])
    if opcde==-1:
        if line[0].upper()=='MOV':
            opcde=MOV(' '.join(line))
            lctr+=opcde                                                     #HAPPY BIRTHDAY TO YOU :D :D :D :D  
        else:
            out+=(line[0]+" is not a valid instruction"+"\n")
            print(line[0]+" is not a valid instruction")
    else:
        lctr+=opcde
        

if __name__=='__main__':
                  
                lctr=0
                sgctr=0
                curseg=''
                out=''
                print("NAME\tOFFSET\tSIZE\tTYPE\tSEGMENT")
                formatting()
                os.startfile("symbol.txt")

with open("symbol.txt",'r') as r:

    csv_read=csv.DictReader(r,delimiter='\t') #reads each line as a dictionary

    with open("symbol_CSV.csv",'w',newline='') as w:
        csv_write=csv.DictWriter(w,delimiter=',',fieldnames=['NAME','OFFSET','SIZE','TYPE','SEGMENT'])
        csv_write.writeheader()
        new_line={}
        for lines in csv_read:
                new_line= {'NAME':lines['NAME'],'OFFSET':lines['OFFSET'],'SIZE':lines['SIZE'],'TYPE':lines['TYPE'],'SEGMENT':lines['SEGMENT']}
                csv_write.writerow(new_line)

                
                    
                        





    
    
    
    




        
        
    










    
    
        
    
        
    
        
    
       
