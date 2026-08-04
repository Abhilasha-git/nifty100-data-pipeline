#from src.dashboard.utils.db import get_cf

#print(get_cf("TCS").head())

#from src.dashboard.utils.db import get_sectors

#print(get_sectors().head())

#from src.dashboard.utils.db import get_peers

#print(get_peers("IT Services").head())

#from src.dashboard.utils.db import get_cf

#print(get_cf("TCS").head())

from src.dashboard.utils.db import get_companies

companies = get_companies()

print(companies.columns.tolist())