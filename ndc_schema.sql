CREATE TABLE "ndc_junction" (
	"ndc_code"	TEXT,
	"brand"	TEXT,
	"strength"	TEXT,
	"dosage"	TEXT,
	PRIMARY KEY("ndc_code")
)
CREATE TABLE "fda_approved" (
	"fda_id"	INTEGER NOT NULL UNIQUE,
	"drug_name"	TEXT,
	"active_ingredients"	TEXT NOT NULL,
	"strength"	TEXT NOT NULL,
	"dosage"	TEXT NOT NULL,
	"route"	TEXT NOT NULL,
	"mrkt_status"	TEXT,
	"te_code"	TEXT,
	"rld"	TEXT,
	"rs"	TEXT,
	"action_date"	TEXT NOT NULL,
	"submission"	TEXT,
	"action_type"	TEXT NOT NULL,
	"ndc_code"	TEXT,
	PRIMARY KEY("fda_id")
)
CREATE TABLE "drug_data" (
	"record_id"	INTEGER NOT NULL UNIQUE,
	"product_ndc"	TEXT,
	"generic_name"	TEXT,
	"labeler_name"	TEXT,
	"brand_name"	TEXT,
	"marketing_category"	TEXT,
	"dosage_form"	TEXT,
	"spl_id"	TEXT,
	"product_type"	TEXT,
	"product_id"	TEXT,
	"application_number"	TEXT,
	"brand_name_base"	TEXT,
	"active_ingredient_name"	TEXT,
	"active_ingredient_strength"	TEXT,
	"route"	TEXT,
	"pharm_class"	TEXT,
	"package_ndc"	TEXT,
	"description"	TEXT,
	"marketing_start_date"	TEXT,
	"listing_expiration_date"	TEXT,
	"sample"	TEXT,
	"finished"	TEXT,
	PRIMARY KEY("record_id")
)
