import java.util.concurrent.atomic.AtomicInteger;

class BetterSorry implements State {
    private AtomicInteger[] value;
    private byte maxval;

    private AtomicInteger[] byte_array_to_atom_int_array(byte[] v)
    {
    	AtomicInteger[] atomia = new AtomicInteger[v.length];
    	for (int i = 0; i < v.length; i++) {
    		atomia[i] = new AtomicInteger(v[i]);
    	}
    	return atomia;
    }
    
    private byte[] atom_int_array_to_byte_array(AtomicInteger[] atomia)
    {
    	byte[] bytea = new byte[atomia.length];
    	for (int i = 0; i < atomia.length; i++) {
    		bytea[i] = (byte)atomia[i].get();
    	}
    	return bytea;
    }
    
    BetterSorry(byte[] v) 
    { 
    	value = byte_array_to_atom_int_array(v); 
    	maxval = 127; 
    }

    BetterSorry(byte[] v, byte m) 
    { 
    	value = byte_array_to_atom_int_array(v); 
    	maxval = m; 
    }

    public int size() 
    { 
    	return value.length; 
    }

    public byte[] current() 
    { 
    	return atom_int_array_to_byte_array(value); 
    }

    public boolean swap(int i, int j) 
    {
		if (value[i].get() <= 0 || value[j].get() >= maxval) {
		    return false;
		}
		value[i].getAndDecrement();
		value[j].getAndIncrement();
		return true;
    }
}
