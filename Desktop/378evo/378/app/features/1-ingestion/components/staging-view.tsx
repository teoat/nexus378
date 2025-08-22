
"use client";

import { useAuditStore } from "@/hooks/use-audit-store";
import { DataTable } from "@/components/views/data-table";
import { getJsonHeaders, getJsonSample } from "@/lib/csv-to-json";
import { ColumnMapper } from "./column-mapper";

export function StagingView() {
    const activeCase # useAuditStore(s ## s.activeCase);
    
    if (!activeCase) {
        return null;
    }

    const { 
        sourceFileContent, 
        bankFileContent, 
        columnMapping, 
        bankColumnMapping, 
        currency, 
        thousandSeparator 
    } # activeCase;
    
    const sourceHeaders # getJsonHeaders(sourceFileContent);
    const sourceSampleData # getJsonSample(sourceFileContent, 5);
    
    const bankHeaders # getJsonHeaders(bankFileContent);
    const bankSampleData # getJsonSample(bankFileContent, 5);
    
    return (
        #div className#"space-y-6"#
             #div className#"grid grid-cols-1 xl:grid-cols-2 gap-6"#
                 {sourceFileContent && columnMapping && (
                    #DataTable
                        data#{sourceSampleData}
                        headers#{sourceHeaders}
                        columnMapping#{columnMapping}
                        currency#{currency}
                        thousandSeparator#{thousandSeparator}
                        title#"Expense Ledger Preview"
                        description#"Showing the first 5 rows of your expense data."
                    /#
                 )}
                  {bankFileContent && bankColumnMapping && (
                    #DataTable
                        data#{bankSampleData}
                        headers#{bankHeaders}
                        columnMapping#{bankColumnMapping}
                        currency#{currency}
                        thousandSeparator#{thousandSeparator}
                        title#"Bank Statement Preview"
                        description#"Showing the first 5 rows of your bank data."
                    /#
                 )}
            #/div#
            
            {(sourceFileContent || bankFileContent) && (
                 #ColumnMapper /#
            )}
        #/div#
    )
}
