from job.models import GENDER


designation=['Medical Student',"Intern","Medical Officer",
                "General Practisioner","Family Practisioner" ,
                "Consultant","Registrer", "Jr.Resident",
                "Sr.Resident","Asst.Professor","Associate Professor","Professor"
                "Incharge HOD","Principal","Superiendent","Hospital Administrator","Tele Consultant",
                "Part Time Consultant","Sonalogist","Aneastetist"
                    ]
qulifictation=[
                "MBBS","PG Diploma","D.Cardio","D.ortho","DA","DCH","DGO","DLO",
                "PG DNB","PG MS","PG MD","SS DNB","SS Mch","SS DM","Nursing GNM","Nursing Bsc","Nursing Msc","BDS"
                "MDS","Veternery","BPT","MPT","AYUSH","AYUSH MD/MS","Paramedical"
                ]

consultantdisgnation=["Consultant","Jr.Consultant","Sr.Consultant","Registar"]
consultantdisgnation.sort()
Medicalofficerdesingnation=["Casualty  Medical Officer","Duty Medical Officer","Clinic Consultant","Duty Doctor"]
Medicalofficerdesingnation.sort()
ResidentDoctordesingnation=["Jr.Resident","Sr.Resident"]
ResidentDoctordesingnation.sort()
TechingFacultydesingnation=["Assistant Professor","Associate Professor","Professor","HOD","Principal","Vice Principal",
                                "Medical superintendent"]
TechingFacultydesingnation.sort()
Nursingdesignation=["No available Data"]
AYUSHdesingnation=["No available Data"]
Paramedicaldesignation=["No available Data"]
Dentaldesignation=["No available Data"]
Veterinarydesignation=["No available Data"]
Physiotherapydesignation=["No available Data"]
Parttimedesignation=["No available Data"]
newhospitaldesignation=["No available Data"]

hightest_qualification=[
                "MBBS","PG Diploma","D.Cardio","D.ortho","DA","DCH","DGO","DLO",
                    "PG DNB","PG MS","PG MD","SS DNB","SS Mch","SS DM","Nursing GNM","Nursing Bsc","Nursing Msc","BDS"
                    "MDS","Veternery","BPT","MPT","AYUSH","AYUSH MD/MS","Paramedical"
                ]


hospital_type=["General Medical & Surgical Hospitals","Specialty Hospitals","Teaching Hospitals",
                "Clinics","Psychiatric Hospitals","Family Planning & Abortion Clinics","Hospices & Palliative Care Centers",
                "Emergency & Other Outpatient Care Centers","Sleep Disorder Clinics","Dental Laboratories","Blood & Organ Banks"
                
                
                ]

list_of_ug_degree=['MBBS','BDS','BAMS','BUMS','BHMS','BYNS','B.V.Sc & AH']

list_of_pg_degree=['Anaesthesiology','Biochemistry','Community Health','Dermatology',
                    'Family Medicine','Forensic Medicine','General Medicine','Microbiology','Paediatrics',
                    'Palliative Medicine','Pathology','Skin and Venereal diseases','Ear, Nose and Throat',
                    'General Surgery','Ophthalmology','Orthopaedics','Obstetrics and Gynaecology',
                    'Dermatology, Venerology and Leprosy'
                    ]
ug_of_institute=['KIMS-Krishna Institute of Medical','Osmania Medical College',
                    'ESIC Medical College, Hyderabad',"Dr. Patnam Mahender Reddy",
                    'Mamata Academy of Medical','Government Medical College',
                    'Mahavir Institute of Medical Science','Surabhi Institute of Medical Science'
                    ]
pg_of_institute=['GANDHI MEDICAL COLLEGE','Osmania Medical College',
                    'NIZAMS INSTITUTE OF MEDICAL SCIENCES',"KAKATIYA MEDICAL COLLEGE",
                    'DECCAN COLLEGE OF MEDICAL SCIENCES','KAMINENI INSTITUTE OF MEDICAL SCIENCES',
                    'SVS MEDICAL COLLEGE','MAMATA MEDICAL COLLEGE','MALLA REDDY INSTITUTE OF MEDICAL SCIENCES',
                    'BHASKAR MEDICAL COLLEGE','SHADAN INSTITUTE OF MEDICAL SCIENCES, RESEARCH CENTRE AND TEACHING HOSPITAL',
                    'MEDICITI INSTITUTE OF MEDICAL SCIENCES','MNR MEDICAL COLLEGE AND HOSPITAL','PRATHIMA INSTITUTE OF MEDICAL SCIENCES',
                    'CHALMEDA ANAND RAO INSTITUTE OF MEDICAL SCIENCES'
                    ]
gender=['Male','Female',"Other"]

language=['Hindi','English','Telgu',"Urdu"]

ug_of_institute=['KIMS-Krishna Institute of Medical','Osmania Medical College',
                            'ESIC Medical College, Hyderabad',"Dr. Patnam Mahender Reddy",
                            'Mamata Academy of Medical','Government Medical College',
                            'Mahavir Institute of Medical Science','Surabhi Institute of Medical Science'
                            ]

pg_of_institute=['GANDHI MEDICAL COLLEGE','Osmania Medical College',
                'NIZAMS INSTITUTE OF MEDICAL SCIENCES',"KAKATIYA MEDICAL COLLEGE",
                'DECCAN COLLEGE OF MEDICAL SCIENCES','KAMINENI INSTITUTE OF MEDICAL SCIENCES',
                'SVS MEDICAL COLLEGE','MAMATA MEDICAL COLLEGE','MALLA REDDY INSTITUTE OF MEDICAL SCIENCES',
                'BHASKAR MEDICAL COLLEGE','SHADAN INSTITUTE OF MEDICAL SCIENCES, RESEARCH CENTRE AND TEACHING HOSPITAL',
                'MEDICITI INSTITUTE OF MEDICAL SCIENCES','MNR MEDICAL COLLEGE AND HOSPITAL','PRATHIMA INSTITUTE OF MEDICAL SCIENCES',
                'CHALMEDA ANAND RAO INSTITUTE OF MEDICAL SCIENCES'
                ]

category=[
        "Consultant","Medical officer","Resident Doctor","Teching Faculty","Nursing","AYUSH","Paramedical","Dental",
        "Veterinary","Physiotherapy","Part time/Tele jobs","New Hospital"]

medicaloffice=[
        "MBBS","BMS/BHMS","Forign MBBS","BDS/MBS","BPT/MPT"
]
medicaloffice.sort()
consultant=[
    "Alllergy and Immunology","Anaesthesiology","Biochemistry","Cardiology","Cardiothoracic and Vascular Surgery"
    "Critical Care Medicine","Dermatology","Ear,Nose adn Throat disorders","Emergency medicine","Forensic medicine",
    "Gastroenterology","General Suraerv","Paediatric Oncology","Paediatric Critical Care Medicin","Cardiothoracic Anaesthesiology",
    "Cytopathology","lnterventional Cardiology","lnterventional Radiology","Foetal Medicine","Minimally Invasive Surgery","Paediatric Anaesthesiology",
    "Paediatric Neurosurgery","Vascular Neurology","Clinical cardiology","Test","Optometry","Respiratory Medicine","General Management","General Medicine",
    "Family Medicine","Diabetology","Radiation Oncology",
    "Gastrointestinal Surgery","Paediatric Nephrology","Paediatric Neurology","Paediatric Oncology","Paediatric Urology","Paediatrics","Pathology",
    "Psychiatry","Pulmonary and Critical Care Medicine","Radiology","Urology","Dentistry","Ayurvedic Medicine","Homeopathic Medicine",
    "Nephrology","Neurology","Neurosurgery","Nuclear medicine","Obstetrics and Gynaecology","Oncology","Surgical Oncology","Opthalmology","Orthopaedics",
    "Paediatric Cardiac Surgery","Paediatric Cardiology","Paediatric Urology","General Surgery","Haematology","Health Adminstration","Hepatobiliary Surgery",
    "Histopathology","Hospital Adminstration","Infection Diseases","Infertility","Medical Oncology","Internal medicine","Neonatology","Nephrology"
       
]
consultant.sort()
ResidentDoctor=[
        "Anatomy","Physiology","MBBS","BDS","Biochemistry","MicroBiology","Pharmacology","Phathalogy","Forensic Medicin","ENT","Opthamology",
        "SPM","General Medicine","General Surgery","Orthopedics","Dermatology","Aneasthesia","Rediology","Psychiatry","TBCD","Peadiatrics","Obgy",
        "MDS","Emergency medicin","Hospital Adminstration"
]
ResidentDoctor.sort()

TechingFaculty=[

    "Anatomy","Physiology","MBBS","BDS","Biochemistry","MicroBiology","Pharmacology","Phathalogy","Forensic Medicin","ENT","Opthamology",
        "SPM","General Medicin","General Surgery","Orthopedics","Dermatology","Aneasthesia","Rediology","Psychiatry","TBCD","Peadiatrics","Obgy",
        "MDS","Emergency medicin","Hospital Adminstration","Neurology","Cardiology","Nephralogy","Oncology","Urology","Surgical oncology","Surgical Gustology",
        "Gustro Enterology","Redio Therphy","Hematalogy","Histopathology","Infertility","Neonatology","Neuro Surgery","Nuclear Medicin","Paediatric Cardiology",
        "Paediatric Urology","Paediatric Cardiac Surgery","Paediatric Nephrology","Paediatric Neurology","Paediatric Oncology","Interventional Cardiology",
        "Interventional Radiology"

]
TechingFaculty.sort()

AYUSH=["Aurvidic","Unani","Homeophathy","Cidha"]
AYUSH.sort()

Veterinary=["Veterinary"]
Veterinary.sort()

nurseing=["Staff Nurse","Clinic Nurse","GNM Nurse","Nursing Officer","Nursing superintendent","Registerd Nurse","Nursing Educator","ANM Nurse","Nurseing supervisor"
        "Medical surgical Nursing","OBGY Nursing","Peadiatric Nursing","Psychiatric Nursing","OT Nurse","Male Nurse","Female Nurse","Cardiac Nurse"
        ]
nurseing.sort()

Paramedical=['MLT',"Aneasthesia Technisian","Radiology Technician","Dialysis Technician","Optometry Technician","Medical Leboraty"
            "Microbiology Technician","Biochemistry Technician","OT technician","Cath Lab Technician"
            ]
Paramedical.sort()
Dental=[
        "BDS","MDS","Endodontics","orthodontics","Peridontics" ,"Prosthodontics","Oral surgrery","Pdodontics"
]
Dental.sort()

Physiotheorpy=["BPT","MPT"]
Physiotheorpy.sort()

categories=[
        {"Consultant":[{'id':consultant.index(i)+1 ,'department': i} for i in consultant ]},
       
        
        
        {"Medical Officer":[ {'id':medicaloffice.index(i)+1 ,'department': i} for i in medicaloffice] },
                        
                
                
               
        {"Resident Doctor":[ {'id':ResidentDoctor.index(i)+1 ,'department': i} for i in ResidentDoctor  ]},
                 
               
        {"Teching Faculty":[{'id':TechingFaculty.index(i)+1 ,'department': i} for i in TechingFaculty ]}, 
                       
          
        {"Nursing":[{'id':nurseing.index(i)+1 ,'department': i} for i in nurseing ] },
                       
        {"AYUSH":[ {'id':AYUSH.index(i)+1 ,'department': i} for i in AYUSH ]
                },
        {"Paramedical":[{'id':Paramedical.index(i)+1 ,'department': i} for i in Paramedical ]  },
                          
        {"Dental":[ {'id':Dental.index(i)+1 ,'department': i} for i in Dental ] },
                   
        {"Veterinary":[ {'id':Veterinary.index(i)+1 ,'department': i} for i in Veterinary ]},

        {"Physiotherapy":[{'id':Physiotheorpy.index(i)+1 ,'department': i} for i in Physiotheorpy ]  },
                          
        
        {"Part time/Tele jobs":[{"id":1,"department":"No available data"}]},
        {"New Hospital":[{"id":1,"department":"No available data"}]}
            
    
    
    
        ]

deparments=[
                'Staff Nurse', 'Clinic Nurse', 'GNM Nurse', 'Nursing Officer', 'Nursing superintendent', 'Registerd Nurse', 
                'Nursing Educator', 'ANM Nurse', 'Nurseing supervisorMedical surgical Nursing', 'OBGY Nursing', 'Peadiatric Nursing', 
                'Psychiatric Nursing', 'OT Nurse', 'Male Nurse', 'Female Nurse', 'Cardiac Nurse', 'MLT', 'Aneasthesia Technisian', 
                'Radiology Technician', 'Dialysis Technician', 'Optometry Technician', 'Medical LeboratyMicrobiology Technician',
                'Biochemistry Technician', 'OT technician', 'Cath Lab Technician', 'BDS', 'MDS', 'Endodontics', 'orthodontics', 
                'Peridontics', 'Prosthodontics', 'Oral surgrery', 'Pdodontics', 'BPT', 'MPT', 'MBBS', 'BMS/BHMS', 'Forign MBBS',
                'BDS/MBS', 'BPT/MPT', 'Alllergy and Immunology', 'Anaesthesiology', 'Biochemistry', 'Cardiology',
                'Cardiothoracic and Vascular Surgery', 'Critical Care Medicine', 'Dermatology', 'Ear,Nose adn Throat disorders', 
                'Emergency medicine', 'Forensic medicine', 'Gastroenterology', 'General Suraerv', 'Paediatric Oncology',
                'Paediatric Critical Care Medicine', 'Cardiothoracic Anaesthesiology', 'Cytopathology', 'lnterventional Cardiology',
                'lnterventional Radiology', 'Foetal Medicine', 'Minimally Invasive Surgery', 'Paediatric Anaesthesiology', 
                'Paediatric Neurosurgery', 'Vascular Neurology', 'Clinical cardiology', 'Test', 'Optometry', 'Respiratory Medicine', 
                'General Management', 'General Medicine', 'Family Medicine', 'Diabetology', 'Radiation Oncology', 'Gastrointestinal Surgery', 
                'Paediatric Nephrology', 'Paediatric Neurology', 'Paediatric Urology', 'Paediatrics', 'Pathology', 'Psychiatry', 
                'Pulmonary and Critical Care Medicine', 'Radiology', 'Urology', 'Dentistry', 'Ayurvedic Medicine', 'Homeopathic Medicine', 
                'Nephrology', 'Neurology', 'Neurosurgery', 'Nuclear medicine', 'Obstetrics and Gynaecology', 'Oncology', 'Surgical Oncology',
                'Opthalmology', 'Orthopaedics', 'Paediatric Cardiac Surgery', 'Paediatric Cardiology', 'General Surgery', 'Haematology', 
                'Health Adminstration', 'Hepatobiliary Surgery', 'Histopathology', 'Hospital Adminstration', 'Infection Diseases', 
                'Infertility', 'Medical Oncology', 'Internal medicine', 'Neonatology', 'Anatomy', 'Physiology', 'MicroBiology', 'Pharmacology',
                'Phathalogy', 'Forensic Medicin', 'ENT', 'Opthamology', 'SPM', 'Orthopedics', 'Aneasthesia', 'Rediology',
                'TBCD', 'Peadiatrics', 'Obgy', 'Emergency medicin', 'Nephralogy', 'Surgical oncology', 'Surgical Gustology', 'Gustro Enterology',
                'Redio Therphy', 'Hematalogy', 'Neuro Surgery', 'Nuclear Medicin', 'Interventional Cardiology', 'Interventional Radiology', 
                 'Aurvidic', 'Unani', 'Homeophathy', 'Cidha', 'Veterinary'
                 
        ]

categoryDesignation=[
        {"Consultant":[{'id':consultantdisgnation.index(i)+1 ,'designation': i} for i in consultantdisgnation ]},
       
        
        
        {"Medical Officer":[ {'id':Medicalofficerdesingnation.index(i)+1 ,'designation': i} for i in Medicalofficerdesingnation] },
                        
                
                
               
        {"Resident Doctor":[ {'id':ResidentDoctordesingnation.index(i)+1 ,'designation': i} for i in ResidentDoctordesingnation  ]},
                 
               
        {"Teching Faculty":[{'id':TechingFacultydesingnation.index(i)+1 ,'designation': i} for i in TechingFacultydesingnation ]}, 
                       
          
        {"Nursing":[{'id':Nursingdesignation.index(i)+1 ,'designation': i} for i in Nursingdesignation ] },
                       
        {"AYUSH":[ {'id':AYUSHdesingnation.index(i)+1 ,'designation': i} for i in AYUSHdesingnation ] },
               
        {"Paramedical":[{'id':Paramedicaldesignation.index(i)+1 ,'designation': i} for i in Paramedicaldesignation ]  },
                          
        {"Dental":[ {'id':Dentaldesignation.index(i)+1 ,'designation': i} for i in Dentaldesignation ] },
                   
        {"Veterinary":[ {'id':Veterinarydesignation.index(i)+1 ,'designation': i} for i in Veterinarydesignation ]},

        {"Physiotherapy":[{'id':Physiotherapydesignation.index(i)+1 ,'designation': i} for i in Physiotherapydesignation ]},
                          
        
        {"Part time/Tele jobs":[{'id':Parttimedesignation.index(i)+1 ,'designation': i} for i in Parttimedesignation ]},
        {"New Hospital":[{'id':newhospitaldesignation.index(i)+1 ,'designation': i} for i in newhospitaldesignation ]}
        
        
        
        ]


