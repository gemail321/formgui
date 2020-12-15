import base64    as b64
from binascii import unhexlify
from GMforms import GMform
from phpserialize import serialize, unserialize
import time
import sys
import os.path


def _obj_decode(s):
    s=b64.b64decode(s)
    s=unhexlify(s.decode())
    return s

def main():
	if (len(sys.argv))<=1:
			print("Usage: formgui.exe <filename.prs>")
			sys.exit(2)

	filein=sys.argv[1]
	namepy=filein.split(sep=".",maxsplit=2)[0]
	dirname=os.path.dirname(filein)
	fileout=namepy+".py"

	print("Convertion: "+filein+" -> "+ fileout)

	with open(filein)  as f:
		  dane=f.read()

	ldane=dane.split(sep="^", maxsplit=5);
	#print(ldane[3])

	lldane=ldane[3].split(sep="#frm#")

	frm=GMform()

	for a in lldane:

		s=_obj_decode(a)
		ds=s.decode().split(sep="#key#", maxsplit=3)
		if (ds[0]=='main'):
			frm.addForm(unserialize(ds[2].encode()))
		elif(ds[0]=='lay'):
			frm.addLayout(ds[1],unserialize(ds[2].encode()))
		elif(ds[0]=='fld'):
			frm.addField(ds[1],unserialize(ds[2].encode()))

	PltObjList={}
	PltParentList={}
	PltWlsList={'0':{'TYP': 'Zero','PARENT_ID_LAY':0}}
	V={}
	for l in frm._arrLayounts:
		VARS=frm.getLayount(l)
		V={}
		for k in VARS:
			V[k.decode()]=VARS[k].decode()

		id_lay=V['ID_LAY']
		PltObjList[id_lay]=''
		PltWlsList[id_lay]=V
		PltParentList[id_lay]=V['PARENT_ID_LAY']

	#print(PltWlsList)
	#print(PltObjList)
	#print(PltParentList)
	mainLayount=''

	for lay in PltObjList:
		parent=PltParentList[lay]

		if (parent=='0'):
			mainLayount+='S_'+lay+'\nLAY_'+lay+'E_'+lay+'\n'
		else:
			if (len(PltObjList[parent])<=0):
				PltObjList[parent]='S_'+lay+'\nLAY_'+lay+'E_'+lay+'\n'
			else:
				PltObjList[parent] +='S_'+lay+'\nLAY_' + lay + 'E_'+lay+'\n'

	for l in PltObjList:
		PltObjList[l]+='LAY_' + l + '\n'

	mainLayount="S_0\n"+mainLayount+"LAY_0\nE_0"

	#print(mainLayount)
	#print(PltWlsList)


	#exit(0)
	while (len(PltObjList)>0):
		PltDelList={}
		for l in PltObjList:
			layount=PltObjList[l]
			if (mainLayount.find('LAY_'+l)>-1):
			   mainLayount=mainLayount.replace('LAY_'+l,layount)
			   #print(mainLayount)
			   PltDelList[l]='1'
			   #print(PltObjList)
		for d in PltDelList:
			  del PltObjList[d]

		#print(PltObjList)

	#print(mainLayount)



	PltFldList={}
	for f in frm._arrFields:
		FLD=frm.getField(f)
		V = {}
		for k in FLD:
			V[k.decode()] = FLD[k].decode()
		id_fld = V['ID_FLD']
		PltFldList[id_fld] = V


	#print(PltFldList)
	#exit(0);

	ReqFldList=[]
	MLFldList=[]

	PaternList={}
	prev_parent='-1'
	start_row=False
	for lay in PltWlsList:
		LAYER=PltWlsList[lay]
		#print(LAYER)
		parent=LAYER['PARENT_ID_LAY']
		parent_typ=PltWlsList[str(parent)]['TYP']
		if  (prev_parent=='-1'):
			prev_parent_typ='Zero'
		else:
			prev_parent_typ = PltWlsList[str(prev_parent)]['TYP']

		typ=LAYER['TYP']
		PaternList['LAY_' + lay]=''
		pre=''
		post=''

		fpre="["
		fpost="],"
		if (typ=="Grid"):
			typ="Row"
		if (parent_typ in ('Row','Grid')):
		   fpre=""
		   fpost=","

		if(typ=='Group'):
			pre='['
			post=']'
			PaternList['S_' + lay] = fpre+"sg.Frame('" + LAYER['TITLE'] + "',\n["
			PaternList['E_' + lay] = "],title_location=sg.TITLE_LOCATION_TOP_LEFT,title_color=self.descr_color, element_justification='"+LAYER['EL_ALIGN']+"',key='-GROUP_" + lay + "-', border_width=1)"+fpost

		elif(typ=='Col'):
			pre = '['
			post = ']'
			PaternList['S_' + lay] = fpre + "sg.Column(["
			PaternList['E_' + lay] = "])" + fpost
		elif(typ=='Zero'):

			PaternList['S_' + lay] = fpre + "sg.Frame('',\n["
			PaternList['E_' + lay] = "],title_location=sg.TITLE_LOCATION_TOP_LEFT, key='-ZERO_" + lay + "-', border_width=0)" + fpost
		else:
			EL_VALIGN = LAYER['EL_VALIGN']
			if (EL_VALIGN not in ('top', 'bottom')):
				EL_VALIGN = 'center'
			PaternList['S_' + lay] =  fpre+"sg.Frame('',\n[["
			PaternList['E_' + lay] = "]],title_location=sg.TITLE_LOCATION_TOP_LEFT,title_color=self.descr_color, element_justification='"+LAYER['EL_ALIGN']+"',vertical_alignment='"+EL_VALIGN+"',key='-ROW_" + lay + "-', border_width=0)"+fpost
		col=0
		field_sep=""
		PaternList['LAY_' + lay]=''
		#print("LAYER:="+LAYER['TNAME']+" "+LAYER['ID_LAY'])
		for f in PltFldList:
			FIELD=PltFldList[f]
			#print(FIELD)
			parent=FIELD['ID_LAY']
			id_lay=FIELD['ID_LAY']
			if (id_lay==lay):

				if (FIELD['TFLD'] in ('TF','PD','TA')):
					if (FIELD['RO']=='1'):
						 disabled=",disabled=True"
					else:
						 disabled=""

					if (FIELD['TFLD']=='PD'):
						pass_char=",password_char='*'"
					else:
						pass_char=""
					try:
						value=FIELD['VAL']
					except:
						value=''
					star="'"
					if (FIELD['REQ']=='1'):
						star="'+self.req_char"
						ReqFldList.append(FIELD['TNAME'])
					if (int(FIELD['LEN'])<=100):
						field_ptrn=pre+"sg.Column(" \
							   "[[sg.T('"+FIELD['DESCR']+star+",size=(None,1),text_color=self.descr_color,key='-"+FIELD['TNAME']+"-')]," \
								"[sg.I(self._set_val(trb,'"+value+"',list_values,'"+FIELD['TNAME']+"'),size=("+FIELD['LEN']+",1)"+disabled+pass_char+",key='"+FIELD['TNAME']+"')]])"+post
					else:
						FIELD['LEN']='100'
						MLFldList.append(FIELD['TNAME'])
						rows=int(int(FIELD['LEN'])/100)+1
						field_ptrn = pre + "sg.Column(" \
										   "[[sg.T('" + FIELD['DESCR']+star + ",size=(None,1),text_color=self.descr_color,key='-" + FIELD[
										 'TNAME'] + "-')]," \
													"[sg.ML(self._set_val(trb,'" + value + "',list_values,'" + FIELD['TNAME'] + "'),size=(" + FIELD['LEN'] + ","+str(rows)+")" + disabled + pass_char + ",key='" + \
									 FIELD['TNAME'] + "')]])" + post


				elif(FIELD['TFLD']=='TX'):
					field_ptrn=pre+"sg.T('"+FIELD['DESCR']+"')"+post
				elif(FIELD['TFLD'] in ('CB','CO')):
					if (FIELD['UNI']=='1'):
						  selected="True"
					else:
						  selected="False"
					field_ptrn=pre+"sg.Checkbox('"+FIELD['VAL']+"', key='"+FIELD['TNAME']+"',default=self._set_val(trb,"+selected+",list_values,'"+FIELD['TNAME']+"',type='boolean'))"+post

				elif(FIELD['TFLD']=='RB'):
					field_ptrn = pre + "sg.Column("
					field_ptrn+="["
					field_ptrn+="\n[sg.Radio('"+FIELD['VAL1']+"','"+FIELD['TNAME']+"',default=self._set_val(trb,True,list_values,'"+FIELD['TNAME']+"1',type='boolean'),key='"+FIELD['TNAME']+"1')],"
					for x in range(2,5):
						try:
							if (len(FIELD['VAL'+str(x)])>0):
								field_ptrn += "\n[sg.Radio('" + FIELD['VAL'+str(x)] + "','" + FIELD['TNAME']+ "',key='"+FIELD['TNAME']+str(x)+"',default=self._set_val(trb,False,list_values,'"+FIELD['TNAME']+str(x)+"',type='boolean'))],"
						except:
							pass
					field_ptrn+="\n])"+post
				elif(FIELD['TFLD']=='BT'):
					field_ptrn=pre+"sg.Button('"+FIELD['DESCR']+"',key='"+FIELD['TNAME']+"')"+post

				elif(FIELD['TFLD']=='DF'):

					field_ptrn = pre + "sg.Column(" \
									   "[[sg.T('" + FIELD['DESCR'] + "',text_color=self.descr_color,size=(18,1))]," \
									   "[sg.I(self._set_val(trb,str(time.strftime('%Y-%m-%d',time.localtime())),list_values,'"+FIELD['TNAME']+"'),enable_events=True,disabled=True,key='"+FIELD['TNAME']+"'" + ",size=(11,1))," \
									   "sg.CalendarButton('x', target=(1,0), format='%Y-%m-%d', default_date_m_d_y=self._set_val('edit',(None,None,None),list_values,'"+FIELD['TNAME']+"',type='date'))]])"+post

				elif(FIELD['TFLD'] in ('LF','La','Lz','LA','LZ')):
					star = "'"
					FIELD['REQ']='1'
					if (FIELD['REQ'] == '1'):
						star="'+self.req_char"
						ReqFldList.append(FIELD['TNAME'])
					field_ptrn = pre + "sg.Column("
					field_ptrn += "["
					field_ptrn += "\n[sg.T('" + FIELD['DESCR'] +star+ ",text_color=self.descr_color,key='-"+FIELD['TNAME']+"-',size=(20,1))],\n"

					if ((FIELD['SIZE']!='1') or (FIELD['MULTI']=='1')):
						if (FIELD['MULTI']=='1'):
							if (FIELD['SIZE']=='1'):
								FIELD['SIZE']='3'
							select_mode="select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE"
						else:
							select_mode = "select_mode=sg.LISTBOX_SELECT_MODE_SINGLE"
						field_ptrn += "[sg.Listbox([['A','a'],['B','b'],['C','c']],default_values=self._set_val(trb,[['B','b']],list_values,'"+FIELD['TNAME']+"',type='list'),disabled=False, size=(20,"+FIELD['SIZE']+"),enable_events=True,"+select_mode+",key='"+FIELD['TNAME']+"')]"
					else:
						field_ptrn += "[sg.Combo([['A','a'],['B','b'],['C','c']],default_value=self._set_val(trb,['B','b'],list_values,'"+FIELD['TNAME']+"',type='list'),disabled=False, size=(20," + FIELD['SIZE'] + "),enable_events=True,key='" + FIELD['TNAME'] + "')]"
					field_ptrn += "\n])" + post
				else:
					field_ptrn=pre+"sg.T('FLD_"+FIELD['TFLD']+"_"+FIELD['ID_FLD']+"')"+post

				PaternList['LAY_'+lay] += field_sep+field_ptrn
				field_sep=","
				prev_parent=parent
				prev_parent_typ = PltWlsList[str(prev_parent)]['TYP']
				#print(field_ptrn)
		#if (len(PaternList['LAY_' + lay])>0):
		#    if ((prev_parent_typ!='Row') and (prev_parent_typ!='Grid') ):
		#        PaternList['LAY_' + lay]=  fpre+PaternList['LAY_'+lay]+fpost


	for p in PaternList:
		body=PaternList[p]

		mainLayount=mainLayount.replace(p,body)

	FormList={}
	for f in frm._arrForm:
		FormList[f.decode()] = frm._arrForm[f].decode()

	func='''
\tdef prepareInsert(self,prefix,fld_list):
\t\tsqlsttm=prefix
\t\tfirst=True
\t\tfor key,val in fld_list.items():
\t\t\tif (first):
\t\t\t\tsqlsttm+=key
\t\t\t\tfirst=False
\t\t\telse:
\t\t\t\tsqlsttm+=","+key
\t\tsqlsttm+=") VALUES ("
\t\tfirst=True
\t\tfor key,val in fld_list.items():
\t\t\tif (first):
\t\t\t\tsqlsttm+="'"+str(val)+"'"
\t\t\t\tfirst=False
\t\t\telse:
\t\t\t\tsqlsttm+=",'"+str(val)+"'"
\t\tsqlsttm+=")"
\t\treturn sqlsttm
\n
\tdef prepareUpdate(self,prefix,fld_list):
\t\tsqlsttm=""
\t\tfirst=True
\t\tfor key,val in fld_list.items():
\t\t\tif (first):
\t\t\t\tsqlsttm+=prefix+key+"='"+str(val)+"'"
\t\t\t\tfirst=False
\t\t\telse:
\t\t\t\tsqlsttm+=","+prefix+key+"='"+str(val)+"'"
\t\treturn sqlsttm
\n


\tdef _set_val(self,trb,v1,lst,fld,**kwargs):
\t\tif trb!='default':
\t\t\tif fld in lst:
\t\t\t\tif ('type' in kwargs):
\t\t\t\t\tif (kwargs['type']=='date'):
\t\t\t\t\t\tif (fld not in lst):
\t\t\t\t\t\t\tlst[fld]=''
\t\t\t\t\t\tif (len(str(lst[fld]).strip())<=0):
\t\t\t\t\t\t\treturn (None,None,None)
\t\t\t\t\t\telse:
\t\t\t\t\t\t\treturn (int(lst[fld].split("-")[1]),int(lst[fld].split("-")[2]),int(lst[fld].split("-")[0]))
\t\t\t\t\telif(kwargs['type']=='boolean'):
\t\t\t\t\t\tif (lst[fld]=='1'):
\t\t\t\t\t\t\treturn True
\t\t\t\t\t\telse:
\t\t\t\t\t\t\treturn False 
\t\t\t\t\telse:
\t\t\t\t\t\treturn lst[fld]
\t\t\t\telse:
\t\t\t\t\treturn lst[fld]
\t\t\telse:
\t\t\t\tif ('type' in kwargs):
\t\t\t\t\tif (kwargs['type']=='list'):
\t\t\t\t\t\treturn []
\t\t\t\t\telif(kwargs['type']=='boolean'):
\t\t\t\t\t\treturn False
\t\t\t\t\telif(kwargs['type']=='date'):
\t\t\t\t\t\tif (fld not in lst):
\t\t\t\t\t\t\tlst[fld]=''
\t\t\t\t\t\tif (len(str(lst[fld]).strip())<=0):
\t\t\t\t\t\t\treturn (None,None,None)
\t\t\t\t\t\telse:
\t\t\t\t\t\t\treturn (int(lst[fld].split("-")[1]),int(lst[fld].split("-")[2]),int(lst[fld].split("-")[0]))
\t\t\t\t\telse:
\t\t\t\t\t\treturn ''
\t\t\t\telse:
\t\t\t\t\treturn ''
\t\telse:
\t\t\treturn v1

'''

	code1='''
\n
\tdef display(self):
\t\twindow = sg.Window('FORM',self.mainLayout, return_keyboard_events=True,modal=True)
\n
\t\twhile True:
\t\t\tevent, values = window.read()
\n
\t\t\tif event=='-OK-':
\n\t\t\t\tprint(event, values)
\n
'''

	code2='''
\t\t\t\t\tvalues[f]=values[f].replace('\\n','')
'''

	code3='''
\t\t\t\tfor f in lst_req:
\t\t\t\t\tif (type(values[f])==str):
\t\t\t\t\t\tvalues[f]=values[f].strip()
\t\t\t\t\tif (len(values[f])<=0):
\t\t\t\t\t\twindow['-'+f+'-'].update(text_color=self.req_color)
\t\t\t\t\t\tif zero_req:
\t\t\t\t\t\t\tpass
\t\t\t\t\t\telse:
\t\t\t\t\t\t\tzero_req=True
\t\t\t\t\t\t\twindow[f].SetFocus(force=True)
\t\t\t\t\telse:
\t\t\t\t\t\twindow['-'+f+'-'].update(text_color=self.descr_color)
\t\t\t\tif (zero_req):
\t\t\t\t\tsg.PopupOK('Please complete all required fields!',title='INFO',modal=True)
\t\t\t\tpass
\t\t\tif event=='-Cancel-':
\t\t\t\tbreak
\t\t\tif (event==None) or (event == sg.WIN_CLOSED):
\t\t\t\tbreak
\t\twindow.close()
\n
\n
\t\nif __name__ == '__main__':
\t\ttrb="default"
\t\tlist_values={}
\t\tfrm=WinForm(trb,list_values)
\t\tfrm.display()
'''

	with open(fileout, 'w', encoding='utf8') as w:
		w.write("import PySimpleGUI as sg")
		w.write("\nimport time")
		w.write("\n\nclass WinForm:")
		w.write("\n\tdef __init__(self,trb,list_values):")
		w.write("\n\n")
		w.write("\n\t\tself.trb=trb")
		w.write("\n\t\tself.list_values=list_values")
		w.write("\n\t\tself.descr_color='white'")
		w.write("\n\t\tself.req_color='yellow'")
		w.write("\n\t\tself.req_char='*'\n")
		w.write("\n\t\tself.mainLayout=[\n")
		w.write(mainLayount)
		w.write("\n[sg.Button('Cancel', key='-Cancel-'), sg.Button('OK', key='-OK-')]")
		w.write("\n]")
		w.write("\n")
		w.write(func)
		w.write(code1)
		w.write("\t\t\t\tfor f in "+str(MLFldList)+":")
		w.write(code2)
		w.write("\t\t\t\tlst_req=" +str(ReqFldList)+'\n')
		w.write("\t\t\t\tzero_req=False")
		w.write(code3)

if __name__ == "__main__":
	main()