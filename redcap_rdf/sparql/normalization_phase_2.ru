# https://dvcs.w3.org/hg/gld/raw-file/default/data-cube/index.html#normalize-algorithm

PREFIX qb: <http://purl.org/linked-data/cube#>

# Dataset attachments
INSERT {
    ?obs  ?comp ?value
} WHERE {
    ?spec    qb:componentProperty ?comp ;
             qb:componentAttachment qb:DataSet .
    ?dataset qb:structure [qb:component ?spec];
             ?comp ?value .
    ?obs     qb:dataSet ?dataset.
};

# Slice attachments
INSERT {
    ?obs  ?comp ?value
} WHERE {
    ?spec    qb:componentProperty ?comp;
             qb:componentAttachment qb:Slice .
    ?dataset qb:structure [qb:component ?spec];
             qb:slice ?slice .
    ?slice ?comp ?value;
           qb:observation ?obs .
};

# Dimension values on slices
INSERT {
    ?obs  ?comp ?value
} WHERE {
    ?spec    qb:componentProperty ?comp .
    ?comp a  qb:DimensionProperty .
    ?dataset qb:structure [qb:component ?spec];
             qb:slice ?slice .
    ?slice ?comp ?value;
           qb:observation ?obs .
}
