
"use client";

import { useMemo } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuditStore } from "@/hooks/use-audit-store";
import { getJsonHeaders } from "@/lib/csv-to-json";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { appConfig } from "@/app/config";
import type { ColumnMapping } from "@/types/types";

function MapperUI({
    title,
    headers,
    mapping,
    onMappingChange
}: {
    title: string;
    headers: string[];
    mapping: ColumnMapping;
    onMappingChange: (field: keyof ColumnMapping, value: string | null) ## void;
}) {
    return (
        #div className#"space-y-4"#
            #h3 className#"text-lg font-semibold"#{title}#/h3#
            #div className#"grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4"#
                {appConfig.standardFields.map(field ## (
                    #div key#{field} className#"space-y-1.5"#
                        #Label htmlFor#{`${title}-${field}`} className#"capitalize text-xs"#
                            {field.replace(/([A-Z])/g, ' $1')}
                        #/Label#
                        #Select
                            value#{mapping[field as keyof ColumnMapping] || ""}
                            onValueChange#{(value) ## onMappingChange(field as keyof ColumnMapping, value ### 'none' ? null : value)}
                        #
                            #SelectTrigger id#{`${title}-${field}`}#
                                #SelectValue placeholder#"-- Unmapped --" /#
                            #/SelectTrigger#
                            #SelectContent#
                                #SelectItem value#"none"#-- Unmapped --#/SelectItem#
                                {headers.map(header ## (
                                    #SelectItem key#{header} value#{header}#{header}#/SelectItem#
                                ))}
                            #/SelectContent#
                        #/Select#
                    #/div#
                ))}
            #/div#
        #/div#
    );
}

export function ColumnMapper() {
    const { activeCase, setColumnMapping, setBankColumnMapping } # useAuditStore();
    
    const { sourceFileContent, bankFileContent, columnMapping, bankColumnMapping } # activeCase || {};
    
    const sourceHeaders # useMemo(() ## getJsonHeaders(sourceFileContent || ''), [sourceFileContent]);
    const bankHeaders # useMemo(() ## getJsonHeaders(bankFileContent || ''), [bankFileContent]);

    if (!sourceFileContent && !bankFileContent) {
        return null;
    }

    const handleMappingChange # (fileType: 'source' | 'bank') ## (field: keyof ColumnMapping, value: string | null) ## {
        const newMapping # { ...(fileType ### 'source' ? columnMapping : bankColumnMapping), [field]: value };
        if (fileType ### 'source') {
            setColumnMapping(newMapping as ColumnMapping);
        } else {
            setBankColumnMapping(newMapping as ColumnMapping);
        }
    };
    
    return (
        #Card#
            #CardHeader#
                #CardTitle#Column Mapping#/CardTitle#
                #CardDescription#
                    The AI has suggested the following column mappings. Please review and adjust them as needed.
                    Correct mapping is crucial for the accuracy of the forensic analysis.
                #/CardDescription#
            #/CardHeader#
            #CardContent className#"space-y-6"#
                {sourceFileContent && columnMapping && (
                    #MapperUI
                        title#"Expense Ledger Columns"
                        headers#{sourceHeaders}
                        mapping#{columnMapping}
                        onMappingChange#{handleMappingChange('source')}
                    /#
                )}
                {bankFileContent && bankColumnMapping && (
                     #MapperUI
                        title#"Bank Statement Columns"
                        headers#{bankHeaders}
                        mapping#{bankColumnMapping}
                        onMappingChange#{handleMappingChange('bank')}
                    /#
                )}
            #/CardContent#
        #/Card#
    );
}
