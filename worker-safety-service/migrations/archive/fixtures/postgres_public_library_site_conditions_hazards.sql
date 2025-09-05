INSERT INTO public.library_hazards (id, name, for_tasks, for_site_conditions) VALUES
	 ('e79c6a50-05e9-4375-9b3d-412dc5172f02', 'Heat illness', false, true),
	 ('e1ae99cc-ffd7-46cc-8bdd-2e6bffa37b8a', 'Frostbite / hypothermia', false, true),
	 ('5a7861e6-948f-451e-8f2e-0c4fc1a2aced', 'Electrocution', false, true),
	 ('de0cc258-75ed-4271-92c1-254edc1bfede', 'Fall to ground ', false, true),
	 ('5c65958a-266a-4f30-b4fa-1da14312aa54', 'Tripping on timber matting', false, true),
	 ('7ca419a8-fa36-43f3-b936-6330a7d7eb39', 'Struck by moving vehicles', false, true),
	 ('b1b09768-2194-493f-ab23-1dc0db20ddc0', 'Immediate medical intervention required', false, true),
	 ('a12b15fd-d553-4eb5-86a6-3d4af789f5c3', 'Congested work space / crowding', false, true),
	 ('9413f34f-91f8-4ae6-b7bc-c56916977337', 'Sabotage / vandalism of equipment ', false, true),
	 ('26362139-0c6e-4405-928d-e84b5d1f3895', 'Transmission of disease / venom', false, true),
	 ('b6829707-53e0-46bb-bfcd-3b749c7d7e85', 'Transmission of venom', false, true),
	 ('3f444e0f-7ea6-4256-acb6-b3a20166652a', 'Contact with wildlife / mauling / death', false, true),
	 ('7621c279-b7df-4b91-b53d-646ff65eac97', 'Fall into water body', false, true),
	 ('6cf6a4fc-b8f9-4335-97c8-c3c8347643d8', 'Drowning', false, true),
	 ('d690719f-f822-4ae5-8cff-c34299d09259', 'Moving equipment / vehicles in a congested area', false, true),
	 ('d2125a81-38bc-4eb5-95a7-0d099068532c', 'Exposure to rotating equipment', false, true),
	 ('90733cdd-2d60-4819-9738-1274af4e3f2c', 'Exposure to buried high pressure utilities', false, true),
	 ('89038c5b-a343-407d-bed6-4f8dd3e874b0', 'Slips,  trips,  and falls due to inadequate lighting', false, true),
	 ('f423ac41-c9a2-4481-b2c0-b6337ea622e0', 'Fall from heights', false, true);

UPDATE public.library_hazards
SET for_site_conditions = true
WHERE id IN ('23b011d4-4cb2-4526-9761-e247d506557a', '179c69cf-2762-4b61-ad3b-36aee3ba9c69', 'c88475a5-e5fc-48a4-904c-6e54a344f647', 'ec37cf5b-26c9-494b-baee-b878ab1cab62');