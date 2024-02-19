typedef long long int wide_int;

namespace pyutil
{
    wide_int bwf(wide_int *val)
    {
        auto inter = ((*val) << 2);
        return inter + (*val);
    }
}
