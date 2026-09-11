from pathlib import Path
p=Path(__file__).with_name('cases_cluster_033.py')
p.write_text(p.read_text().replace('tippaṛ̆','tippuṛ̆').replace('p acce','pacce'))
