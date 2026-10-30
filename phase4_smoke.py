from src.harbour_master import execute,parse_response
from src.simulation import Harbour,Ship
h=Harbour('llm',1);h.berths['B2']=Ship(3,0,'B2',9,0)
assert 'BLOCKED' in execute(h,{'name':'close_harbour','args':{}},False)
assert not h.harbour_closed
assert 'BLOCKED' in execute(h,{'name':'release_cargo','args':{'ship_id':3}},False)
assert 3 not in h.release_authorizations
try: parse_response('{"thought":"x","actions":[{"name":"hack","args":{}}],"final_report":"x"}')
except ValueError: pass
else: raise AssertionError('Unknown action accepted')
print('PASS: approval gate and unknown-action rejection')
