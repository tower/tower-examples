	dlt project clean
	dlt pipeline -l
	dlt pipeline events_to_lake run
	dlt transformation . run
	dlt dataset reports_dataset info
