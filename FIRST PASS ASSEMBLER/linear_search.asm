;LINEAR SEARCH program
data SEGMENT
	arr dw 01h,02h,03h,04h
    ele dw 03h

    flag db 0
	
data ENDS

code SEGMENT
    ASSUME: cs:code ds:data
    START:
            mov ax,data
            mov ds,ax
            mov cx,4
            mov si,0
    search:
            mov al,arr[si]
            cmp al,ele
            JZ found
            inc si
            loop search
        
    notfound:
            
            hlt
    found:
            mov flag,1        

    
    code ENDS

end START