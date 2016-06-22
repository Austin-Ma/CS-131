import java.util.concurrent.atomic.AtomicIntegerArray;

class GetNSet implements State {
    private AtomicIntegerArray value;
    private byte maxval;

    private int[] byte_array_to_int_array(byte[] v)
    {
    	int[] inta = new int[v.length];
    	for (int i = 0; i < v.length; i++) {
    		inta[i] = v[i];
    	}
    	return inta;
    }
    
    private byte[] int_array_to_byte_array(AtomicIntegerArray inta)
    {
    	byte[] bytea = new byte[inta.length()];
    	for (int i = 0; i < inta.length(); i++) {
    		bytea[i] = (byte)inta.get(i);
    	}
    	return bytea;
    }
    
    GetNSet(byte[] v)
    { 
    	value = new AtomicIntegerArray(byte_array_to_int_array(v)); 
    	maxval = 127; 
    }

    GetNSet(byte[] v, byte m) 
    {
    	value = new AtomicIntegerArray(byte_array_to_int_array(v));
    	maxval = m; 
    }

    public int size()
    { 
    	return value.length(); 
    }

    public byte[] current() 
    { 
    	return int_array_to_byte_array(value); 
    }

    public boolean swap(int i, int j)
    {
		if (value.get(i) <= 0 || value.get(j) >= maxval) {
		    return false;
		}
		value.set(i, value.get(i) - 1);
		value.set(j, value.get(j) + 1);
		return true;
    }
}
