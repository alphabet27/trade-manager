--%view=trsc_summary_fy_new
--%
SELECT
    sb.BILL, sb.INVOICE_DATE,
    sb.ALIAS, p.PARTY_NAME, sb.NARR,
    ROUND(SUM(sf.QTY*sf.RATE - sf.QTY*sf.RATE*sf.DISC/100 +
    sf.QTY*sf.RATE*sf.GST/100 - sf.QTY*sf.RATE*sf.DISC*sf.GST/10000), 2)
    AS "AMOUNT"
FROM
    trsc_billdata_fy sb
JOIN
    party_db p ON sb.ALIAS = p.ALIAS
LEFT JOIN
    trsc_fulldata_fy sf ON sb.BILL = sf.BILL
GROUP BY
    sb.BILL --, sb.INVOICE_DATE, p.PARTY_NAME, sb.NARR
ORDER BY
    sb.BILL ASC;
--%

--%view=hsn_summary_view
--%
SELECT 
	fd.BILL AS BILL,
	bd.INVOICE_DATE AS INVOICE_DATE,
	bd.ALIAS AS ALIAS,
    pd.HSN_CODE as HSN_CODE,
	fd.GST as GST,
	ROUND(SUM(fd.QTY*fd.RATE - fd.QTY*fd.RATE*fd.DISC/100), 2) as "TAXABLE"
FROM 
	fulldata_table AS fd
JOIN 
	product_db as pd ON fd.PID = pd.PID
JOIN 
	billdata_table as bd ON fd.BILL = bd.BILL
GROUP BY 
	fd.BILL, pd.HSN_CODE
ORDER BY
    pd.HSN_CODE, fd.BILL
--%


--%view=ledger_alias
--%
-- Query for specific alias
SELECT
    "BILL No." AS "BILL/PAY_ID", "Date",
    "Type", "PAY_MODE", "Amount",
    SUM("Amount") OVER (
        ORDER BY "Date",
        CASE WHEN "Type" = 'Invoice' THEN 1 ELSE 2 END
        ROWS UNBOUNDED PRECEDING
    ) AS "Balance"
FROM (
    -- Bills
    SELECT
        sb.BILL AS "BILL No.",
        sb.INVOICE_DATE AS "Date",
        'Invoice' AS "Type",
        "" AS "PAY_MODE",
        ROUND(COALESCE(SUM(
            sf.QTY*sf.RATE - sf.QTY*sf.RATE*sf.DISC/100
		+ sf.QTY*sf.RATE*sf.GST/100 - sf.QTY*sf.RATE*sf.DISC*sf.GST/10000
        ), 0), 2) AS "Amount"
    FROM billdata_table sb
    LEFT JOIN fulldata_table sf ON sb.BILL = sf.BILL
    WHERE sb.ALIAS = ?  -- Parameter for alias
    GROUP BY sb.BILL, sb.INVOICE_DATE

    UNION ALL

    -- Payments
    SELECT
        PAY_ID AS "BILL No.",
        PAY_DATE AS "Date",
        'Payment' AS "Type",
        PAY_MODE AS "PAY_MODE",
        -ROUND(AMOUNT, 2) AS "Amount"
    FROM payments_table
    WHERE ALIAS = ?  -- Same parameter
)
ORDER BY "Date",
    CASE WHEN "Type" = 'Invoice' THEN 1 ELSE 2 END;

--%

--%query=transaction_form_query
--%
select
	s.PID, p.GST_D, p.HSN_CODE, p.MFG, p.UNIT,
	s.BATCH, s.EXPIRY, s.MRP, s.BAL
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
	s.TID, s.BILL, s.SR_NO, s.PID,
	p.PRODUCT_NAME, p.HSN_CODE, p.MFG,
	p.UNIT, s.GST, s.QTY, s.RATE, s.DISC,
	(s.QTY*s.RATE  - s.QTY*s.RATE*s.DISC/100) AS "TAXABLE",
	s.BATCH, s.EXPIRY, s.MRP
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

--%stats
--%
SELECT name, pageno, pgsize FROM dbstat where name="sale_fulldata_fy_25";
--%
