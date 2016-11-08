#######################################################################################################
##	Topological sort

from functools import reduce

def tsort(data):
	for k, v in data.items():
		v.discard(k)  # Ignore self dependencies
	extra_items_in_deps = reduce(set.union, data.values()) - set(data.keys())
	data.update({item: set() for item in extra_items_in_deps})
	while True:
		ordered = set(item for item, dep in data.items() if not dep)
		if not ordered:
			break
		yield ' '.join(sorted(ordered))
		data = {item: (dep - ordered) for item, dep in data.items()
				if item not in ordered}
	assert not data, "A cyclic dependency exists amongst %r" % data

########################################################################################################

if __name__ == "__main__":

#	## Budget
	budget = dict(
				Reg2={''}
#			,	IsScoring = {'f.ScLane'}
#			,	IsHW66 = {'f.IsAMULane'}
#			,	IsSuiteSpot = {'f.SuiteSpotLane'}
#			,	IsTenpinTour = {'f.TenPT'}
#			,	IsBESXDualMode = {'f.BESXDM'}
#			,	IsTenpinTourUPG = {'f.TenPTUPG'}
#			,	IsBESXDualModeUPG = {'f.BESXDMUPG'}
#			,	IsCProUPG = {'f.IsUpgLic'}
#			,	IsUPG = {'f.ScUpgLane'}
#			,	IsAMFScTrdIn = {'f.Is_tradein'}
#			,	ProductLine2 = {'f.ScoreFamily'}
#			,	_ScoreFamily_2 = {'f.ScoreFamily_2'}
#			,	_ScoreFamily_3 = {'f.ScoreFamily_3'}
			,	OrderDateCheck = {'OrderY', 'OrderM', '_CurY', '_CurM'}
			,	ShippedDateCheck = {'InvoiceY', 'InvoiceM', '_CurY', '_CurM'}
			,	ShippedMonthCheck = {'InvoiceM', '_CurM'}
			,	Test = {'InvoiceY', 'OrderY'}
			,	YearOfRef = {'InvoiceY', 'OrderM', '_CurM', 'OrderY', '_CurY'}
			,	YSH = {'InvoiceM', '_CurM', 'InvoiceY'}
			,	_ExchRate={'_ExchRateY', '_ExchRateM'}
			,	_ExchRateY = {'InvoiceY', '_CurY'}
			,	_ExchRateM = {'InvoiceY', '_CurY', 'InvoiceM', '_CurM'}
			,	_SumIsUPG = {'s._SumIsUPG'}
			,	_SumIsAMFScTrdIn = {'s._SumIsAMFScTrdIn'}
			,	_SumIsHW66 = {'s._SumIsHW66'}
			,	_SumIsScoring = {'s._SumIsScoring'}
			,	_SumIsCProUPG = {'s._SumIsCProUPG'}
			,	_SumIsAMFConv = {'s._SumIsAMFConv'}
			,	_SumIsBrunConv = {'s._SumIsIsBrunConv'}
			,	_SumTPTThroughBESXDMUPG = {'IsTenpinTour', 'IsBESXDualMode', 'IsTenpinTourUPG', 'IsBESXDualModeUPG'}
			,	IsOrdWAMFConv = {'s._SumIsAMFConv'}
			,	IsOrdWBrunConv = {'s._SumIsBrunConv'}
			,	MainProductFamily = {'IsSuiteSpot', 'IsHW66', '_ScoreFamily_2'}
			,	MainProductLine = {'IsHW66', 'IsSuiteSpot', '_ScoreFamily_2'}
			,	MainProductLine2 = {'IsHW66', 'IsSuiteSpot', '_ScoreFamily_3'}
			,	IsScPlusIsHW = {'IsScoring', 'IsHW66', '_SumTPTThroughBESXDMUPG'}
			,	IsOrdWUpg = {'IsScoring', '_SumIsUPG'}
			,	SubReg1 = {'USSubRegNoMil', 'SubReg'}
			,	IsOrdWAMFScTrdIn = {'IsScoring', '_SumIsAMFScTrdIn'}
#			,	UniqueOrder = {'uo.MainOrder'}
			,	YBL = {'IsScPlusIsHW', 'IsCProUPG', 'IsSuiteSpot', '_SumTPTThroughBESXDMUPG', 'InvoiceY', 'OrderY', '_CurY', 'OrderM', '_CurM', 'InvoiceM'}
			,	MainProductFamily2 = {'MainProductFamily'}
			,	IsToBeCounted = {'IsScoring', 'IsHW66', 'IsSuiteSpot', '_SumTPTThroughBESXDMUPG'}
			,	PrjType = {'_SumIsHW66', '_SumIsScoring', 'IsOrdWUpg', 'IsOrdWAMFScTrdIn', 'IsOrdWAMFConv', 'IsOrdWBrunConv', '_SumIsCProUPG', 'MainPrLine', '_SumIsScoring'}
			,	Ord = {'IsScPlusIsHW'}
			,	SH = {'YSH', 'IsScPlusIsHW'}
			,	BL = {'YBL', 'IsScPlusIsHW'}
			,	BudgetClm = {'YSH', 'YBL', '_IncludeAllOrders', 'YPromised', '_CurY'}
			,	YBL1 = {'YBL', 'OrderY', 'OrderM', '_CurM'}
			,	YBL2 = {'YBL', 'OrderY', 'OrderM', '_CurM'}
			,	YBLBDG = {'YBL', '_IncludeAllOrders', 'YPromised', '_CurY', 'YPromised'}
			,	MainOPF2 = {'MainProductFamily2'}
			,	UMOPF = {'MainProductFamily2'}
			,	UMOPFAMU = {'MainProductFamily2'}
			,	UniqueOrderCProUPG = {'PrjType', 'UniqueOrder', '_SumIsCproUpg'}
			,	PrjTypeBudget = {'PrjType'}
			,	DistrPartner = {'PrjType', 'SubReg1'}
			,	RevUSD = {'YSH', 'YBLBDG', '_ExchRate'}
			,	BL1 = {'YBL1', 'IsScPlusIsHW'}
			,	BL2 = {'YBL2', 'IsScPlusIsHW'}
			,	AMERSubReg = {'MacroReg', 'DistrPartner', 'USSubRegNoMil'}	# , 'ur.Region'}
			,	MajorDistPartner = {'PrjType', 'SubReg1', 'DistrPartner'}
			,	QtyIncl = {'SH', 'BL', 'BL1', 'BL2'}
			,	TotBL = {'BL', 'BL1', 'BL2'}
			,	LookupListPrice = {'RevUSD'}
			,	SubReg2 = {'MajorDistPartner', 'SubReg1'}
			,	AdjSalesRepRegion = {'AMERSubReg', 'AMERSubReg'}
			,	SHBL = {'SH', 'TotBL'}
			,	BLCY = {'TotBL', '_IncludeAllOrders', 'YPromised', '_CurY', 'TotBL'}
			,	LineTotalListPrice = {'YSH', 'YBLBDG', 'LookupListPrice', 'LookupListPrice', 'RevUSD', 'LookupListPrice'}
			,	BLNY = {'TotBL', 'BLCY'}
			,	ListUSD = {'LineTotalListPrice', 'YSH', 'YBLBDG', 'RevUSD', '_ExchRate'}
	)

	## Lanes
	lanes = dict(
				OrderDateCheck={'OrderY', 'OrderM', '_CurY', '_CurM'}
			,	ShippedDateCheck={'InvoiceY', 'InvoiceM', '_CurY', '_CurM'}
			,	Test={'InvoiceY', 'OrderY'}
			,	YearOfRef={'InvoiceY', 'OrderM', '_CurM', '_CurY'}
			,	_ExchRateY={'InvoiceY', '_CurY'}
			,	_ExchRateM={'InvoiceY', 'InvoiceM', '_CurM'}
			,	SumIsUPG={'IsUPG'}
			,	SumIsAMFScTrdIn={'IsAMFScTrdIn'}
			,	SumIsHW66={'IsHW66'}
			,	SumIsScoring={'IsScoring'}
			,	SumIsCProUPG={'IsCProUPG'}
			,	SumIsAMFConv={'IsAMFConv'}
			,	SumIsBrunConv={'IsBrunConv'}
			,	IsHWY66Theme={'IDTheme'}
			,	IsOrdWAMFConv={'SumIsAMFConv'}
			,	IsOrdWBrunConv={'SumIsBrunConv'}
			,	OrderNumHWY66Theme={'IsHWY66Theme', 'IDTheme'}
			,	ProductFamily={'IsSuiteSpot', 'IsHW66', '_ScoreFamily'}
			,	_SumTPTThroughBESXDMUPG={'IsTenpinTour', 'IsBESXDualMode', 'IsTenpinTourUPG', 'IsBESXDualModeUPG'}
			,	IsScPlusIsHW={'IsScoring', 'IsHW66', '_SumTPTThroughBESXDMUPG'}
			,	IsOrdWUpg={'IsScoring', 'SumIsUPG'}
			,	IsOrdWAMFScTrdIn={'IsScoring', 'SumIsAMFScTrdIn'}
			,	SubReg1={'USSubReg', 'SubReg'}
			,	MainProductFamily={'IsSuiteSpot', 'IsHW66', '_ScoreFamily_2'}
			,	OrderHWY66Theme = {'ProductFamily'}
			,	YBL = {'IsScPlusIsHW', 'IsCProUPG', 'IsSuiteSpot', '_SumTPTThroughBESXDMUPG', 'InvoiceY', 'OrderY', '_CurY', 'OrderM', '_CurM', 'InvoiceM'}
			,	Ord = {'IsScPlusIsHW', 'IsScPlusIsHW'}
			,	PrjType = {'SumIsHW66', 'SumIsScoring', 'IsOrdWUpg', 'IsOrdWAMFScTrdIn', 'IsOrdWAMFConv', 'IsOrdWBrunConv', 'MainPrLine', 'SumIsCProUPG'}
			,	HWY66Theme = {'ProductFamily', 'OrderHWY66Theme'}
			,	DistrPartner = {'PrjType', 'SubReg1'}
			,	YBL1 = {'YBL', 'IsScPlusIsHW', 'IsCProUPG', 'IsSuiteSpot', '_SumTPTThroughBESXDMUPG', 'OrderY', 'OrderM', '_CurM'}
			,	YBL2 = {'YBL', 'IsScPlusIsHW', 'IsCProUPG', 'IsSuiteSpot', '_SumTPTThroughBESXDMUPG', 'OrderY', 'OrderM', '_CurM'}
			,	BL = {'YBL', 'IsScPlusIsHW'}
			,	YSH = {'PrjType', 'UniqueOrder', 'IsScPlusIsHW', 'IsSuiteSpot', '_SumTPTThroughBESXDMUPG', 'InvoiceM', '_CurM', 'InvoiceY'}
			,	BL1 = {'YBL1', 'IsScPlusIsHW'}
			,	BL2 = {'YBL2', 'IsScPlusIsHW'}
			,	SH = {'YSH', 'IsScPlusIsHW'}
			,	AMERSubReg = {'MacroReg', 'DistrPartner', 'USSubRegNoMIL', 'SubReg'}
			,	MajorDistPartner = {'PrjType', 'SubReg1', 'DistrPartner'}
			,	QtyIncl = {'SH', 'BL', 'BL1', 'BL2'}
			,	TotBL = {'BL', 'BL1', 'BL2'}
			,	CYBL = {'YBL', '_CurY', 'AMERSubReg', 'BL'}
			,	AdjSalesRepRegion = {'AMERSubReg'}
			,	SubReg2 = {'MajorDistPartner', 'SubReg1'}
			)

	n = 0
	for i in tsort(budget):
		for j in i.split(): print(n, j)
		print()
		n += 1
