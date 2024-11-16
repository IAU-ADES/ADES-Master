from ades.packUtil import programCodesArray

def test_programCodesArray():
    program_code_mappings = "\n".join([f"{i} {i}" for i in range(10)])
    # copied from https://www.minorplanetcenter.net/iau/lists/ProgramCodes.txt
    program_code_mappings += R"""
    !  10    A  42    a  68
    "  11    B  43    b  69
    #  12    C  44    c  70
    $  13    D  45    d  71
    %  14    E  46    e  72
    &  15    F  47    f  73
    '  16    G  48    g  74
    (  17    H  49    h  75
    )  18    I  50    i  76
    *  19    J  51    j  77
    +  20    K  52    k  78
    ,  21    L  53    l  79
    -  22    M  54    m  80
    .  23    N  55    n  81
    /  24    O  56    o  82
    [  25    P  57    p  83
    \  26    Q  58    q  84
    ]  27    R  59    r  85
    ^  28    S  60    s  86
    _  29    T  61    t  87
    `  30    U  62    u  88
    {  31    V  63    v  89
    |  32    W  64    w  90
    }  33    X  65    x  91
    ~  34    Y  66    y  92
    :  35    Z  67    z  93
    ;  36
    <  37
    =  38
    >  39
    ?  40
    @  41
    """
    mapping = {}
    v = None
    for i, c in enumerate((" ".join(program_code_mappings.strip().split("\n"))).split()):
        if i % 2 == 0:
            k = c
            v = None
        else:
            v = int(c)
        if v is not None:
            mapping[k] = v

    # sort mapping by values
    mapping = {k: v for k, v in sorted(mapping.items(), key=lambda x : x[1])}
    for k in programCodesArray:
        if k == "£": # £ has no defined mapping yet
            continue
        assert(k in mapping)

    for k in mapping:
        assert(mapping[k] == programCodesArray.index(k))
