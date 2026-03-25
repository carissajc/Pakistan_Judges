* match prim_keys to shachar's data

use "data_shachar",replace
collapse id,by(prim)
sort id
save id_prim,replace

use data_ces,replace

sort id
merge 1:1 id using id_prim
drop _merge

sort prim

save data_ces_matched,replace

* now put together main data
use "C:\Users\rfisman\BOSTON UNIVERSITY Dropbox\Raymond Fisman\Pakistan Judges Experiment\Data\data0922.dta",replace

* get rid of tests etc
egen order=group(begin)
keep if order>197

* merge in ces data

sort prim_key
merge 1:1 prim_key using data_ces_matched 
drop _merge

* did they enter their name?
g name=in_personal2~=""
drop if in_personal2=="test"
drop if name==0

* first, we get data for shachar to calculate alpha, garp, etc

* get better variable names for x,y,xmax,ymax
forvalues d=1/10 {
	foreach z in x y {
	g `z'_1`d'=selectedpoint`z'_`d'_
	g `z'_2`d'=selectedpoint`z'_2_`d'_
	g `z'max_1`d'=line`z'_`d'_
	g `z'max_2`d'=line`z'_2_`d'_
} 	
	ren phase2reorder_`d'_ reorder`d'

}

preserve
keep prim_key id x_11 - ymax_210 reorder*

reshape long x_1 x_2 y_1 y_2 xmax_1 xmax_2 ymax_1 ymax_2 reorder, i(id) j(decision)


* generate measure of fraction to cheaper account and to x
forvalues s=1/2 {
	g xcheaper_`s'=xmax_`s'/ymax_`s' > 1
	g xfrac_`s'=x_`s'/(x_`s'+y_`s')
	g frac_cheaper_`s'=xfrac_`s' if xcheaper_`s'==1
	replace frac_cheaper_`s'=1-xfrac_`s' if xcheaper_`s'==0

}

collapse frac_cheaper* xfrac_*,by(id) 
sort id
save fractions,replace

restore
merge 1:1 id using fractions
tab _merge
drop _merge

* bring in measures of vignette legal implications
preserve
use vignettes_raw,clear
* normalize each object
foreach t in c d e f {
	foreach v in 1 2 3 4 {
		foreach o in min max mean {
		egen `o'_`t'`v'=`o'(`t'`v')
		}
		g `t'`v'_normalized=(`t'`v'-mean_`t'`v')
		*/(max_`t'`v'-min_`t'`v')
	}
}

sort n
keep *normalized n
save vignettes_normalized,replace

restore


preserve
keep prim vg002-vg005_4

* vignette 4 choice is missing
* vg002 corresponds to the *first* vignette
* so we do some reordering/renaming

keep if vg002~=""

foreach v in 2 {
	foreach n in 1 2 3 4 {
		ren vg00`v'_`n' vignette1`n'
	}
}

foreach v in 3 {
	foreach n in 1 2 3  {
		ren vg00`v'_`n' vignette2`n'
	}
}

foreach v in 4 {
	foreach n in 1 2 3 {
		ren vg00`v'_`n' vignette3`n'
	}
}

foreach v in 5 {
	foreach n in 1 2 3 4 {
		ren vg00`v'_`n' vignette4`n'
	}
}

reshape long vignette1 vignette2 vignette3 vignette4,i(prim) j(n)

* bring in normalized measures
sort n
merge n:1 n using vignettes_normalized

* now calculate cross-product for each set of responses for each notion of justice

foreach t in c d e f {
	foreach v in 1 2 3 4 {
		g temp=vignette`v'*`t'`v'
		egen `t'`v'_score=mean(temp),by(prim)
		drop temp
	}
	g `t'_score=(`t'1_score+`t'2_score+`t'3_score+`t'4_score)/4
}

collapse c_score d_score e_score f_score,by(prim)

sort prim_key
save justice_scores,replace
restore

sort prim_key
merge 1:1 prim_key using justice_scores

* normalize equality-efficiency survey questions

* adjust so higher --> more efficiency

g gap1=sa011-sa009
g gap2=sa015-sa013

foreach var in sa009 sa013 sa028 {
	replace `var'=10-`var'
}
foreach var in sa009 sa011 sa013 sa015 sa028 gap1 gap2 {
	
	egen av_`var'=mean(`var')
	egen sd_`var'=sd(`var')
	g `var'_norm=(`var'-av_`var')/sd_`var'
	drop av_`var' sd_`var'
}

g eq_focus=(sa009_norm+sa011_norm+sa013_norm+sa015_norm+sa028_norm)/5

corr sa009_norm - sa028_norm eq_focus gap1 gap2

* rho adjustment
g rho_adj=r1d if r1d>=0
replace rho_adj=-log(1-r1d) if r1d<0
egen rho_rank=rank(r1d)
corr rho_rank rho_adj eq_focus sa009_norm - sa028_norm 

end here


