typedef long long int64_t;

namespace pyutil
{
    int64_t bwf(int64_t *val)
    {
        auto inter = ((*val) << 2);
        return inter + (*val);
    }
}
