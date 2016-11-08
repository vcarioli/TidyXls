from tokenizer import XlsParser, XlsTokens

############################################

expr = (
        'IF(OR([@MainOrder]="Exclude",OrderNumber=10),ROW(),"NO")'
    ,   'IF(AND([@MainOrder]="Exclude",[@OrderType]="S0",OR(NUMBERVALUE([@OrderNumber])=-15811206,NUMBERVALUE([@OrderNumber])=15810892),NUMBERVALUE([@OrderNumber])=15811372),"TRUE","FALSE")'
    ,   'IF([@MainOrder]="Exclude","_",IF(IFERROR(OR([@OrderType]="S0",NUMBERVALUE([@OrderNumber])=15811206,NUMBERVALUE([@OrderNumber])=15810892,NUMBERVALUE([@OrderNumber])=15811372),FALSE),"RENT",IF(SUMIF(JDEDataTable[[MainOrder]:[MainOrder]],[@MainOrder],JDEDataTable[[IsHW66]:[IsHW66]])>0,IF(SUMIF(JDEDataTable[[MainOrder]:[MainOrder]],[@MainOrder],JDEDataTable[[IsScoring]:[IsScoring]])>0,"HW66-BES X","HW66"),IF([@IsOrdWUpg]>0,IF([@IsOrdWAMFScTrdIn]>0,"Q/AMF UPG","Q/AMF UPG"),IF([@IsOrdWBrunConv]>0,"MOD BRW",IF(SUMIF(JDEDataTable[[MainOrder]:[MainOrder]],[@MainOrder],JDEDataTable[[IsScoring]:[IsScoring]])>0,IF([@MainPrLine]="STS",IF(MID([@OrderType],2,1)="3","MOD","NCP"),"HW66-BES X"),IF(SUMIF(JDEDataTable[[MainOrder]:[MainOrder]],[@MainOrder],JDEDataTable[[IsCProUPG]:[IsCProUPG]])>0,"CProUPG",IF([@MainPrLine]="STS",IF(SUMIF(JDEDataTable[[MainOrder]:[MainOrder]],[@MainOrder],JDEDataTable[[IsScoring]:[IsScoring]])>0,"MOD","Other MOD"),"HW66"))))))))'
)

def print_tokens(tokens):
    fmt = '{0:15}   {1:13}   {2}'
    print(fmt.format('TOKEN TYPE', 'TOKEN SUBTYPE', 'TOKEN VALUE'))
    print('----------------- --------------- ---------------------------------')
    for t in tokens:
        print(fmt.format(t.ttype, t.tsubtype, t.tvalue))
    print('----------------- --------------- ---------------------------------')


if __name__ == '__main__':
    for e in expr:
        print_tokens(XlsParser(e).items)
        print(XlsParser(e, ';').xlstidy())
        print()

