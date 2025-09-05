INSERT INTO public.library_site_conditions (id, name) VALUES
	 ('edb8f382-f825-49d8-adc6-11b7deae686c', 'Roadway closed for work (roadclosed)');

UPDATE public.library_site_conditions as existing SET
	handle_code = new.handle_code
	FROM (VALUES
	 ('b4d9101d-28d1-4265-ab6a-22b6957638a8', 'heat_index'),
	 ('b9a1bc0e-0152-41e7-b14e-10172fa09a11', 'cold_index'),
	 ('6ef7ba5e-cdcf-4a04-aa5d-b339fd54c6c5', 'lightning_forecast'),
	 ('0e36249c-28a7-4454-809b-33cbd4b2880f', 'slip'),
	 ('242195fb-e4ef-4d72-ada6-d7ccb7078ec5', 'environment_sensitive'),
	 ('85ddce3d-d2cf-490b-be25-7f3e68997de1', 'roadway'),
	 ('6fcc5b80-cfa5-4097-b03e-44eed04dd9dd', 'traffic_density'),
	 ('7774b205-ad0c-4ce4-86e1-51a2762d8602', 'hospital_distance'),
	 ('427ab836-1d51-4535-bfa4-6f08085b9c9f', 'cell_coverage'),
	 ('024ff047-1ab4-4fa5-8a4f-c1f57277a4a4', 'population_density'),
	 ('bb0246ec-84a9-450e-8103-b29e62ac3349', 'crime'),
	 ('b61df9d0-4d8f-49ff-8b2c-34fafa950bdc', 'insects'),
	 ('76a65257-7697-46db-b28a-6d229bae79ba', 'snakes'),
	 ('211d23ac-127a-4c5a-9c53-6c1ff6b28ee5', 'bears'),
	 ('406e2587-94f4-4225-a727-fb4025bc5add', 'working_over_water'),
	 ('7d4e6780-6710-4249-a3ab-1765c6975e50', 'other_constructions'),
	 ('8157bb4b-f85c-45a0-9fda-7ea0c5d75830', 'work_near_regulator_station'),
	 ('c0a84add-44b8-49e4-895e-9300eb711b46', 'working_at_night'),
	 ('c121e8ed-3629-42cb-b355-ae7f747569d0', 'elevated_row'),
	 ('932b4861-1901-46d2-874e-ec717b908a5a', 'exposure_active_road'),
	 ('edb8f382-f825-49d8-adc6-11b7deae686c', 'road_closed')
	) as new(id, handle_code)
WHERE existing.id::text = new.id;