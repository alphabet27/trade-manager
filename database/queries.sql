--%view=trsc_summary_fy_new
--%
SELECT
    sb.BILL,
    sb.INVOICE_DATE,
    sb.ALIAS,
    p.PARTY_NAME,
    sb.NARR,
    SUM(sf.QTY * sf.RATE) AS "TAXABLE"
FROM
    trsc_billdata_fy sb
JOIN
    party_db p ON sb.ALIAS = p.ALIAS
LEFT JOIN
    trsc_fulldata_fy sf ON sb.BILL = sf.BILL
GROUP BY
    sb.BILL, sb.INVOICE_DATE, p.PARTY_NAME, sb.NARR
ORDER BY
    sb.BILL ASC;
--%

--%query=transaction_form_query
--%
select
	s.PID,
	p.GST_D,
	p.HSN_CODE,
	p.MFG,
	p.UNIT,
	s.BATCH,
	s.EXPIRY,
	s.MRP,
	s.BAL
FROM
	product_db p
JOIN
	stock_db s ON p.PID = s.PID
ORDER BY
	p.PID ASC;
--%

--%view=transaction_summary_billno
--%
SELECT
	s.TID,
	s.BILL,
	s.SR_NO,
	s.PID,
	p.PRODUCT_NAME,
	p.HSN_CODE,
	p.MFG,
	p.UNIT,
	s.GST,
	s.QTY,
	s.RATE,
	s.DISC,
	s.QTY * s.RATE * (1 - (s.DISC)/100) AS "TAXABLE",
	s.BATCH,
	s.EXPIRY,
	s.MRP
FROM
	trsc_fulldata_fy s
JOIN
	product_db p ON s.PID = p.PID
WHERE
	s.BILL = ?
ORDER BY
	s.SR_NO ASC;
--%

--%add_to_table=table_name%new_row
--%
INSERT OR REPLACE INTO
	table_name cols
VALUES
	new_row;
--%

--%delete_row=table_name
--%
DELETE FROM
	table_name
WHERE
	col_name=?;
--%

--%load_history=fy_id%alias%pid
--%
SELECT
	fd.BILL, fd.QTY, fd.RATE, fd.DISC,
	fd.GST, fd.BATCH, fd.EXPIRY, fd.MRP
FROM
	(
	SELECT * FROM
		fulldata_table fdt
	WHERE
		fdt.PID=?
	) fd
JOIN
	billdata_table bd ON fd.BILL = bd.BILL
WHERE
	bd.ALIAS=?;
--%


